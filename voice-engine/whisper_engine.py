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
        self.cpu_threads: int = 4  # overridable before calling load() — see EngineSettings

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
            download_root=self.config.download_root,  # pinned persistent cache in serve mode —
                            # see VoiceEngineServer.__init__ — so the model is only ever
                            # downloaded once per machine, regardless of Windows user
                            # profile / OS cache quirks.
        )
        self._warm_up()
        self.load_time = time.perf_counter() - t0
        return self.load_time

    def _warm_up(self) -> None:
        """
        Run one throwaway inference on ~0.5s of silence right after loading.
        The first real call into a freshly-loaded CTranslate2 model pays a
        one-time allocation/JIT cost — better to eat that here than on the
        first actual customer utterance.
        """
        try:
            dummy = np.zeros(int(16000 * 0.5), dtype=np.float32)
            segments, _ = self._model.transcribe(dummy, language=self.config.language, beam_size=1)
            list(segments)  # force evaluation
        except Exception:
            pass  # warm-up is best-effort — never let it block startup

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
        1. Cyclic n-gram repetition — catches multi-word loops ANYWHERE in
           the text, e.g. "وینستون مارلبرو بهمن کنت پرلبرو بهمن کنت پرلبرو…"
           (cycle length 1–6 words, loop may start after a clean prefix —
           it does NOT need to start at word 0).
        2. Repeated-word coverage — catches "کامل کامل کامل…" as well as
           cases where two or three words alternate/repeat enough to fill
           most of the text even without one single word dominating.
        3. Absurd total length — a short utterance should never produce
           120+ words.
        """
        words = [w for w in text.split() if w]
        n = len(words)
        if n == 0:
            return False

        # --- Heuristic 1: cyclic repetition of length 1..6, starting ANYWHERE ---
        max_cycle = min(6, n // 2)
        for start in range(0, n - 1):
            for cycle_len in range(1, max_cycle + 1):
                if start + cycle_len * 2 > n:
                    continue
                cycle = words[start:start + cycle_len]
                repeats = 0
                i = start
                while i + cycle_len <= n and words[i:i + cycle_len] == cycle:
                    repeats += 1
                    i += cycle_len
                covered = repeats * cycle_len
                # 3+ full repeats covering a good chunk of the text → loop,
                # even if it doesn't start at word 0 (a clean prefix like
                # "وینستون مارلبرو" followed by a loop still counts).
                if repeats >= 3 and covered / n > 0.4:
                    return True
                # Only 2 full repeats, but they cover almost the entire
                # remaining text (e.g. an 8-word utterance that is really
                # just a 3-word phrase said twice) → also a loop.
                if repeats >= 2 and covered / n > 0.7:
                    return True

        # --- Heuristic 1b: whole utterance is the same short phrase said
        # twice back-to-back (e.g. "داناهیل داناهیل") — too short for the
        # cycle scan above to reach repeats>=2 with covered/n>0.7 when
        # n is small, so check it directly.
        if n >= 2 and n % 2 == 0:
            half = n // 2
            if words[:half] == words[half:]:
                return True

        # --- Heuristic 2: repeated-word coverage ---
        # Sum of the top-2 most common words' counts vs. total length —
        # catches loops built from 2-3 alternating brand words where no
        # single word individually clears an old, stricter threshold.
        counts = Counter(words).most_common(2)
        top_count = sum(c for _, c in counts)
        if counts and counts[0][1] >= 3 and top_count / n > 0.5:
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
            without_timestamps=True,  # we never use segment timestamps — skip computing them
            word_timestamps=False,
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