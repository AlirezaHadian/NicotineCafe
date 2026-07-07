"""
whisper_engine.py — faster-whisper wrapper for Persian STT.

Includes a two-stage hallucination guard:
  1. VAD filter strips silence before it ever reaches the model
     (the #1 cause of repetition loops on short/quiet recordings).
  2. Post-hoc cycle detection catches any loop that still slips through
     (e.g. "آبی قرمز سفید آبی قرمز سفید…").
"""
from __future__ import annotations

import time
from collections import Counter
from pathlib import Path
from typing import Optional, Union

import numpy as np

try:
    from faster_whisper import WhisperModel
except ImportError as e:
    raise ImportError("Install faster-whisper:  pip install faster-whisper") from e

from config import WhisperConfig


class TranscriptionResult:
    """Structured result from a single transcription call."""
    __slots__ = ("text", "language", "inference_time", "segments", "is_hallucination")

    def __init__(
        self,
        text: str,
        language: str,
        inference_time: float,
        segments: list[dict],
        is_hallucination: bool = False,
    ) -> None:
        self.text = text
        self.language = language
        self.inference_time = inference_time
        self.segments = segments
        self.is_hallucination = is_hallucination

    def __repr__(self) -> str:
        return (
            f"TranscriptionResult(text={self.text!r}, "
            f"time={self.inference_time:.3f}s, "
            f"hallucination={self.is_hallucination})"
        )


class WhisperEngine:
    """
    Single-instance faster-whisper wrapper with hallucination guard.
    """

    def __init__(self, config: WhisperConfig) -> None:
        self.config = config
        self._model: Optional[WhisperModel] = None
        self.load_time: float = 0.0
        self.cpu_threads: int = 2  # overridable before calling load() — see EngineSettings

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------

    def load(self) -> float:
        t0 = time.perf_counter()
        self._model = WhisperModel(
            self.config.model_size,
            device="cpu",
            compute_type=self.config.compute_type,
            cpu_threads=self.cpu_threads,  # NOTE: more threads is NOT always faster for small models —
                            # oversubscription can add scheduling overhead that dominates
                            # the actual compute. Tune this per-machine if needed.
        )
        self.load_time = time.perf_counter() - t0
        return self.load_time

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def ensure_loaded(self) -> None:
        if not self.is_loaded:
            self.load()

    # ------------------------------------------------------------------
    # Hallucination detection
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_hallucination(text: str) -> bool:
        """
        Returns True when the text looks like a Whisper repetition loop.

        Three heuristics, in order:
        1. Cyclic n-gram repetition — catches multi-word loops like
           "آبی قرمز سفید آبی قرمز سفید…" (cycle length 1–6 words).
        2. Single dominant word — catches "کامل کامل کامل…".
        3. Absurd total length — a short utterance should never produce
           120+ words.
        """
        words = [w for w in text.split() if w]
        n = len(words)
        if n == 0:
            return False

        # --- Heuristic 1: cyclic repetition of length 1..6 ---
        max_cycle = min(6, n // 2)
        for cycle_len in range(1, max_cycle + 1):
            cycle = words[:cycle_len]
            repeats = 0
            i = 0
            while i + cycle_len <= n and words[i:i + cycle_len] == cycle:
                repeats += 1
                i += cycle_len
            covered = repeats * cycle_len
            # 3+ full repeats covering most of the text → loop
            if repeats >= 3 and covered / n > 0.6:
                return True

        # --- Heuristic 2: single dominant word ---
        # Requires an actual minimum repeat count (3+) so short, normal
        # sentences (e.g. 2-word utterances) aren't falsely flagged just
        # because one word happens to be 1-of-2.
        most_common_count = Counter(words).most_common(1)[0][1]
        if most_common_count >= 3 and most_common_count / n > 0.35:
            return True

        # --- Heuristic 3: absurd length ---
        if n > 120:
            return True

        return False

    # ------------------------------------------------------------------
    # Transcription
    # ------------------------------------------------------------------

    def transcribe(
        self,
        audio: Union[np.ndarray, str, Path],
        *,
        initial_prompt: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio with VAD pre-filtering + post-hoc hallucination guard.
        Returns empty text (is_hallucination=True) instead of looped garbage.
        """
        self.ensure_loaded()
        assert self._model is not None

        if isinstance(audio, np.ndarray) and audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0

        prompt = initial_prompt if initial_prompt is not None else self.config.initial_prompt

        t0 = time.perf_counter()
        segments_gen, info = self._model.transcribe(
            audio,  # type: ignore[arg-type]
            language=self.config.language,
            condition_on_previous_text=self.config.condition_on_previous_text,
            temperature=self.config.temperature,
            beam_size=self.config.beam_size,
            best_of=self.config.best_of,
            initial_prompt=prompt,
            no_speech_threshold=self.config.no_speech_threshold,
            compression_ratio_threshold=self.config.compression_ratio_threshold,
            log_prob_threshold=self.config.log_prob_threshold,
            vad_filter=self.config.vad_filter,
            vad_parameters=dict(min_silence_duration_ms=self.config.vad_min_silence_ms),
        )

        # Iterate manually instead of list(segments_gen): a hallucination loop
        # shows up as the SAME short segment text repeating over and over.
        # Bail out the instant we see that pattern (or a hard time budget is
        # exceeded) instead of waiting for the model to generate hundreds of
        # repeated tokens before we're allowed to discard them — this is what
        # made hallucinating calls take 4-9s instead of ~2s.
        raw_segments = []
        last_text: Optional[str] = None
        repeat_run = 0
        deadline = t0 + 3.5  # hard cap regardless of what's happening
        for seg in segments_gen:
            raw_segments.append(seg)
            seg_text = seg.text.strip()
            if seg_text and seg_text == last_text:
                repeat_run += 1
                if repeat_run >= 2:  # same short phrase 3x in a row = looping
                    break
            else:
                repeat_run = 0
            last_text = seg_text
            if time.perf_counter() > deadline:
                break

        inference_time = time.perf_counter() - t0

        text = " ".join(seg.text.strip() for seg in raw_segments).strip()
        seg_dicts = [
            {"start": s.start, "end": s.end, "text": s.text}
            for s in raw_segments
        ]

        is_hallucination = self._detect_hallucination(text)
        if is_hallucination:
            print(f"  ⚠ Hallucination detected — output discarded.")
            text = ""

        return TranscriptionResult(
            text=text,
            language=info.language,
            inference_time=inference_time,
            segments=seg_dicts,
            is_hallucination=is_hallucination,
        )

    def transcribe_file(self, path: Union[str, Path]) -> TranscriptionResult:
        return self.transcribe(str(path))