"""
recorder.py — Microphone audio recorder.

Press and HOLD the SPACE bar to record; release to stop.
Captured audio is saved as a 16 kHz / mono / PCM-16 WAV file
inside the configured ``recordings/`` directory.

Dependencies: sounddevice, keyboard, numpy
"""
from __future__ import annotations

import queue
import time
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import sounddevice as sd
except ImportError as e:
    raise ImportError("Install 'sounddevice':  pip install sounddevice") from e

from config import RecorderConfig


class AudioRecorder:
    """
    Space-bar triggered microphone recorder.

    Usage
    -----
    recorder = AudioRecorder(config)
    audio, path = recorder.record_and_save()   # blocking call
    """

    def __init__(self, config: RecorderConfig, level_callback=None) -> None:
        """
        level_callback : Optional[Callable[[float], None]]
            If given, called on every audio chunk while recording with the
            chunk's RMS level normalised to roughly 0.0–1.0. Used to drive
            the WPF equalizer over the socket bridge — purely additive,
            never affects recognition.
        """
        self.config = config
        self.config.recordings_dir.mkdir(parents=True, exist_ok=True)
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._level_callback = level_callback

    # ------------------------------------------------------------------
    # Internal callback
    # ------------------------------------------------------------------

    def _sd_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status,
    ) -> None:
        """sounddevice stream callback — enqueues incoming audio chunks."""
        if status:
            # Non-fatal: log and continue
            print(f"  [Recorder] Stream status: {status}", flush=True)
        self._queue.put(indata.copy())

        if self._level_callback is not None:
            rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2)))
            normalised = min(1.0, rms / 3000.0)  # int16 scale, empirically tuned
            self._level_callback(normalised)

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def _drain_queue(self) -> list[np.ndarray]:
        """Collect all pending frames from the internal queue."""
        chunks: list[np.ndarray] = []
        while True:
            try:
                chunks.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return chunks

    def record(self) -> Optional[np.ndarray]:
        """
        Block until SPACE is pressed, record while held, stop on release.

        Returns
        -------
        np.ndarray or None
            Flat int16 array of audio samples, or None if nothing captured.
        """
        # Flush stale queue content
        self._drain_queue()

        try:
            import keyboard
        except ImportError as e:
            raise ImportError("Install 'keyboard':  pip install keyboard") from e

        print(">>> Hold SPACE to record  (release to stop) ...", end="", flush=True)
        keyboard.wait("space")
        print("  ● REC", end="", flush=True)

        stream_kwargs = dict(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            callback=self._sd_callback,
        )

        with sd.InputStream(**stream_kwargs):
            # Stay open while SPACE is held
            while keyboard.is_pressed("space"):
                time.sleep(0.01)
            # Grab a tiny extra tail to avoid cutting off trailing audio
            time.sleep(self.config.post_silence_s)

        print("  ■ STOP", flush=True)

        chunks = self._drain_queue()
        if not chunks:
            print("  [Recorder] No audio captured.")
            return None

        audio = np.concatenate(chunks, axis=0).flatten()
        duration = len(audio) / self.config.sample_rate
        print(f"  Captured {duration:.2f}s  ({len(audio):,} samples)")
        return audio

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------

    def save_wav(
        self,
        audio: np.ndarray,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Persist *audio* as a PCM-16 WAV file.

        Parameters
        ----------
        audio:
            1-D int16 numpy array.
        filename:
            Optional explicit filename (without directory). A timestamp-based
            name is generated when omitted.

        Returns
        -------
        Path
            Full path to the saved file.
        """
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rec_{ts}.wav"

        path = self.config.recordings_dir / filename

        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(2)  # int16 → 2 bytes per sample
            wf.setframerate(self.config.sample_rate)
            wf.writeframes(audio.astype(np.int16).tobytes())

        print(f"  Saved → {path}")
        return path

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def record_and_save(self) -> tuple[Optional[np.ndarray], Optional[Path]]:
        """
        Record from microphone, save, and return both the audio array
        and the path to the saved file.
        """
        audio = self.record()
        if audio is None or audio.size == 0:
            return None, None
        path = self.save_wav(audio)
        return audio, path


class ControlledRecorder:
    """
    Explicit start()/stop() microphone recorder — no global keyboard hook,
    no admin rights needed. Used by server.py: the WPF app tells us exactly
    when to start and stop via the TCP bridge (e.g. a push-to-talk button
    or mic icon in the UI), instead of Python listening for a SPACE press
    that requires elevated privileges to register system-wide on Windows.
    """

    def __init__(self, config: RecorderConfig, level_callback=None) -> None:
        self.config = config
        self.config.recordings_dir.mkdir(parents=True, exist_ok=True)
        self._level_callback = level_callback
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: Optional[sd.InputStream] = None

    def _sd_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            print(f"  [Recorder] Stream status: {status}", flush=True)
        self._queue.put(indata.copy())
        if self._level_callback is not None:
            rms = float(np.sqrt(np.mean(indata.astype(np.float32) ** 2)))
            self._level_callback(min(1.0, rms / 3000.0))

    def start(self) -> None:
        if self._stream is not None:
            return  # already recording
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            callback=self._sd_callback,
        )
        self._stream.start()

    def stop(self) -> Optional[np.ndarray]:
        """Stop capture and return the recorded audio (or None if empty)."""
        if self._stream is None:
            return None
        time.sleep(self.config.post_silence_s)
        self._stream.stop()
        self._stream.close()
        self._stream = None

        chunks: list[np.ndarray] = []
        while True:
            try:
                chunks.append(self._queue.get_nowait())
            except queue.Empty:
                break
        if not chunks:
            return None
        return np.concatenate(chunks, axis=0).flatten()

    @property
    def is_recording(self) -> bool:
        return self._stream is not None
