"""
recorder.py — Microphone audio recorder.

Press and HOLD the SPACE bar to record; release to stop.
Captured audio is saved as a 16 kHz / mono / PCM-16 WAV file
inside the configured ``recordings/`` directory.

Dependencies: sounddevice, keyboard, numpy
"""
from __future__ import annotations

import queue
import threading
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


class AutoVadRecorder:
    """
    Always-on microphone listener with a simple energy-based VAD state machine.
    No start()/stop() commands needed from the UI — this runs continuously in
    the background and calls `utterance_callback(audio: np.ndarray)` every
    time it detects a complete spoken utterance (speech onset -> silence).

    This replaces the push-to-talk ControlledRecorder for the default
    "customer walks up and talks" retail flow: the operator/customer never
    touches a button, the mic is always listening.

    Tuning knobs (pass at construction time, defaults chosen from real
    logged audio_level ranges: background noise ~0.02-0.04, speech ~0.1-0.9):
      speech_threshold   : RMS level above which we consider "speech started"
      silence_hangover_s : how much continuous quiet before we call it "done"
      pre_roll_s         : audio kept from just BEFORE the threshold trip,
                            so the first phoneme of the utterance isn't cut off
      max_utterance_s    : hard cap so a long noise burst can't hang forever
      min_utterance_s    : discard anything shorter (coughs, clicks, taps)
    """

    def __init__(
        self,
        config: RecorderConfig,
        utterance_callback,
        level_callback=None,
        speech_threshold: float = 0.09,     # was 0.07 — fewer false triggers on background noise
        silence_hangover_s: float = 0.55,
        pre_roll_s: float = 0.2,
        max_utterance_s: float = 6.0,
        min_utterance_s: float = 0.9,       # was 0.5 — short blips (taps/breath) never reach Whisper now
    ) -> None:
        self.config = config
        self._utterance_callback = utterance_callback
        self._level_callback = level_callback
        self._speech_threshold = speech_threshold
        self._silence_hangover_s = silence_hangover_s
        self._pre_roll_chunks = max(1, int(pre_roll_s / 0.02))  # ~20ms per chunk at typical blocksize
        self._max_utterance_s = max_utterance_s
        self._min_utterance_s = min_utterance_s

        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._worker: Optional[threading.Thread] = None
        self._running = False
        self._paused = False

    def pause(self) -> None:
        """Stop reacting to speech, but keep the mic stream open so resume() is instant."""
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    def _sd_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            print(f"  [AutoVadRecorder] Stream status: {status}", flush=True)
        chunk = indata.copy()
        self._queue.put(chunk)
        if self._level_callback is not None:
            rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
            self._level_callback(min(1.0, rms / 3000.0))

    def _chunk_rms_norm(self, chunk: np.ndarray) -> float:
        rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
        return min(1.0, rms / 3000.0)

    def _worker_loop(self) -> None:
        pre_roll: list[np.ndarray] = []
        utterance: list[np.ndarray] = []
        in_speech = False
        silence_time = 0.0
        speech_time = 0.0
        chunk_duration = 0.0

        while self._running:
            try:
                chunk = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if chunk_duration == 0.0:
                chunk_duration = len(chunk) / self.config.sample_rate

            if self._paused:
                # Drop everything while paused — don't track onset/offset,
                # don't buffer, don't call back. Stream stays open so
                # resume() is instant (no re-opening the mic device).
                in_speech = False
                utterance = []
                pre_roll = []
                continue

            level = self._chunk_rms_norm(chunk)

            if not in_speech:
                pre_roll.append(chunk)
                if len(pre_roll) > self._pre_roll_chunks:
                    pre_roll.pop(0)
                if level >= self._speech_threshold:
                    in_speech = True
                    utterance = list(pre_roll)
                    speech_time = 0.0
                    silence_time = 0.0
                continue

            # in_speech == True
            utterance.append(chunk)
            speech_time += chunk_duration
            if level < self._speech_threshold:
                silence_time += chunk_duration
            else:
                silence_time = 0.0

            if silence_time >= self._silence_hangover_s or speech_time >= self._max_utterance_s:
                audio = np.concatenate(utterance, axis=0).flatten() if utterance else None
                in_speech = False
                utterance = []
                pre_roll = []
                if audio is not None and (len(audio) / self.config.sample_rate) >= self._min_utterance_s:
                    # Run the (potentially slow, especially on hallucination
                    # loops) callback in its own thread so THIS worker loop
                    # keeps tracking real-time speech onset/offset instead of
                    # falling behind and merging unrelated utterances together.
                    threading.Thread(
                        target=self._safe_invoke_callback, args=(audio,), daemon=True
                    ).start()

    def _safe_invoke_callback(self, audio: np.ndarray) -> None:
        try:
            self._utterance_callback(audio)
        except Exception as ex:  # never let a bad utterance kill the listener
            print(f"  [AutoVadRecorder] utterance_callback error: {ex!r}", flush=True)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            blocksize=int(self.config.sample_rate * 0.03),  # ~30ms chunks — fewer, larger callbacks
            latency="high",  # more internal buffering so a busy CPU (mid-transcribe)
                              # doesn't cause "input overflow" / dropped audio
            callback=self._sd_callback,
        )
        self._stream.start()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._worker is not None:
            self._worker.join(timeout=2)
            self._worker = None
