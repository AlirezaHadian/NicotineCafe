"""
config.py — Central configuration for VoiceBenchmark.
All tuneable parameters live here. No magic numbers in business logic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ModelSize = Literal["tiny", "base", "small"]
ALL_MODEL_SIZES: list[ModelSize] = ["tiny", "base", "small"]


@dataclass
class WhisperConfig:
    """Settings passed directly to faster-whisper."""
    model_size: ModelSize = "tiny"   # tiny = ~3-5x faster than base on CPU; small accuracy drop.
                                      # If accuracy matters more than speed on capable hardware,
                                      # override with --model base or --model small.
    language: str = "fa"
    beam_size: int = 1     # 1 = greedy decoding, much faster; raise to 5 for max accuracy if speed allows
    best_of: int = 1       # only affects temperature>0 sampling — unused while temperature=0.0
    condition_on_previous_text: bool = False
    temperature: float = 0.0
    compute_type: str = "int8"

    # --- Hallucination / silence guards ---
    no_speech_threshold: float = 0.6
    compression_ratio_threshold: float = 2.0
    log_prob_threshold: float = -1.0

    # VAD disabled: our own hallucination detector is sufficient,
    # and faster-whisper's VAD is too aggressive for short brand names
    # like کنت / کمل said in isolation.
    vad_filter: bool = True   # let faster-whisper's internal Silero VAD reject
                              # non-speech audio fast, instead of hallucinating
                              # through it for several seconds before we catch it
    vad_min_silence_ms: int = 300

    initial_prompt: str = (
        "وینستون مارلبرو بهمن کنت پارلیامنت ال ام رویال داناهیل کامل اولترالایت"
    )


@dataclass
class RecorderConfig:
    """Audio capture settings."""
    sample_rate: int = 16_000
    channels: int = 1
    dtype: str = "int16"
    recordings_dir: Path = Path("recordings")
    post_silence_s: float = 0.3
    # Recordings shorter than this are almost certainly accidental
    # taps / noise and are skipped before ever reaching Whisper.
    min_duration_s: float = 0.6


@dataclass
class MatcherConfig:
    """Fuzzy matching thresholds and weights."""
    brand_weight: float = 0.70
    variant_weight: float = 0.30
    # Brand names (وینستون، مارلبرو) are distinctive → lower threshold OK
    fuzzy_threshold: float = 76.0
    # Variant words (آبی، گلد) are common Persian words → need higher bar
    # to avoid matching filler verbs like داری، بده against دبل، گلد
    variant_fuzzy_threshold: float = 82.0
    min_confidence: float = 0.60  # raised from 0.48 — filters out low-confidence noise matches
                                   # (garbled/unrelated speech incorrectly mapped to a brand)


@dataclass
class AppConfig:
    """Top-level config assembled from sub-configs."""
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    recorder: RecorderConfig = field(default_factory=RecorderConfig)
    matcher: MatcherConfig = field(default_factory=MatcherConfig)

    brands_file: Path = Path("brands.json")
    variants_file: Path = Path("variants.json")
    results_dir: Path = Path("results")
    samples_dir: Path = Path("samples")
    debug: bool = False

    def resolve_paths(self, base: Path | None = None) -> "AppConfig":
        root = base or Path.cwd()
        self.recorder.recordings_dir = root / self.recorder.recordings_dir
        self.brands_file = root / self.brands_file
        self.variants_file = root / self.variants_file
        self.results_dir = root / self.results_dir
        self.samples_dir = root / self.samples_dir
        return self