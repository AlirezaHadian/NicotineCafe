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
    model_size: ModelSize = "small"   # accuracy-first default (per current testing).
                                      # tiny = ~3-5x faster than base on CPU but noticeably
                                      # worse on accented/short Persian speech. Switch back
                                      # to "tiny" (via EngineSettings, no code change needed)
                                      # if latency ever becomes the priority instead.
    language: str = "fa"
    beam_size: int = 5     # higher beam = better accuracy for a real but bounded speed
                            # cost. Also overridable at runtime via EngineSettings.
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

    # IMPORTANT: keep this as domain *context*, not an enumerable list of
    # exact brand names. faster-whisper tends to echo initial_prompt tokens
    # verbatim during silent/noisy segments — the previous prompt (a bare
    # word-list of brand names, including some not even in the catalog)
    # was the direct cause of hallucinated output like "وینستون مارلبرو
    # بهمن کنت پرلبرو بهمن کنت..." and "داناهیل داناهیل داناهیل".
    initial_prompt: str = (
        "مکالمه مشتری با فروشنده در یک مغازه دخانیات درباره نام برند سیگار."
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
    """Fuzzy matching thresholds — brand-only recognition."""
    # Brand names (وینستون، مارلبرو) are distinctive → this is the only
    # threshold that matters now; variant/model matching was removed.
    fuzzy_threshold: float = 76.0
    min_confidence: float = 0.65  # was 0.60 — a bit stricter now that alias
                                   # collisions (e.g. Blake vs Captain Black) are fixed


@dataclass
class AppConfig:
    """Top-level config assembled from sub-configs."""
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    recorder: RecorderConfig = field(default_factory=RecorderConfig)
    matcher: MatcherConfig = field(default_factory=MatcherConfig)

    brands_file: Path = Path("brands.json")
    results_dir: Path = Path("results")
    samples_dir: Path = Path("samples")
    debug: bool = False

    def resolve_paths(self, base: Path | None = None) -> "AppConfig":
        root = base or Path.cwd()
        self.recorder.recordings_dir = root / self.recorder.recordings_dir
        self.brands_file = root / self.brands_file
        self.results_dir = root / self.results_dir
        self.samples_dir = root / self.samples_dir
        return self