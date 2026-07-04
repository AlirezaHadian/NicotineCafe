"""
main.py — Entry point for VoiceBenchmark.

Modes
-----
  mic        Record from microphone (hold SPACE) and detect product.
  file       Detect product from one or more WAV files.
  benchmark  Run multi-model benchmark.
  explain    Debug mode: full pipeline trace for text or WAV.

Usage
-----
  python main.py mic
  python main.py --model tiny mic --loops 5
  python main.py file samples/test.wav
  python main.py benchmark --models tiny base
  python main.py explain --text "ونستون آبی میخوام"
  python main.py explain --file recordings/rec.wav
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import AppConfig, WhisperConfig, ALL_MODEL_SIZES, ModelSize


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_result(result, inference_time: float | None = None) -> None:  # type: ignore
    r = result
    sep = "─" * 54
    print(sep)
    print(f"  Recognised   : {r.raw_text!r}")
    print(f"  Normalised   : {r.normalised_text!r}")
    print(f"  Brand        : {r.brand_match.brand or '—'}"
          f"  (score: {r.brand_match.score:.0%})")
    print(f"  Variant      : {r.variant_match.variant or '—'}"
          f"  (score: {r.variant_match.score:.0%})")
    print(f"  Confidence   : {r.product.confidence:.0%}")
    if inference_time is not None:
        print(f"  Infer time   : {inference_time:.3f}s")
    print()
    if r.is_valid:
        print(f"  ✅  محصول: {r.product.product_name}")
    else:
        print("  ❌  محصولی شناسایی نشد")
    print(sep)


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------

def mode_mic(args: argparse.Namespace, config: AppConfig) -> None:
    from recorder import AudioRecorder
    from whisper_engine import WhisperEngine
    from matcher import ProductMatcher

    recorder = AudioRecorder(config.recorder)
    engine = WhisperEngine(config.whisper)
    matcher = ProductMatcher(config)

    print(f"\n  Loading Whisper [{config.whisper.model_size}] …", end="", flush=True)
    load_time = engine.load()
    print(f"  {load_time:.2f}s\n")

    loops = getattr(args, "loops", 0)
    iteration = 0
    try:
        while loops == 0 or iteration < loops:
            iteration += 1
            audio, path = recorder.record_and_save()
            if audio is None:
                continue

            duration_s = len(audio) / config.recorder.sample_rate
            if duration_s < config.recorder.min_duration_s:
                print(f"  ⚠ ضبط خیلی کوتاه بود ({duration_s:.2f}s) — دوباره امتحان کن\n")
                continue

            transcription = engine.transcribe(audio)

            if transcription.is_hallucination or not transcription.text.strip():
                print("  ⚠ صدا واضح نبود — دوباره امتحان کن\n")
                continue

            result = matcher.match(transcription.text)
            print_result(result, transcription.inference_time)

    except KeyboardInterrupt:
        print("\n  [Stopped by user]")


def mode_file(args: argparse.Namespace, config: AppConfig) -> None:
    from whisper_engine import WhisperEngine
    from matcher import ProductMatcher

    paths = [Path(p) for p in args.input]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"  Error: file(s) not found: {missing}", file=sys.stderr)
        sys.exit(1)

    engine = WhisperEngine(config.whisper)
    matcher = ProductMatcher(config)

    print(f"\n  Loading Whisper [{config.whisper.model_size}] …", end="", flush=True)
    load_time = engine.load()
    print(f"  {load_time:.2f}s\n")

    for path in paths:
        print(f"\n  File: {path.name}")
        transcription = engine.transcribe_file(path)
        if transcription.is_hallucination or not transcription.text.strip():
            print("  ⚠ صدا قابل تشخیص نبود\n")
            continue
        result = matcher.match(transcription.text)
        print_result(result, transcription.inference_time)


def mode_serve(args: argparse.Namespace, config: AppConfig) -> None:
    """
    Production mode: starts the TCP bridge consumed by the WPF app
    (NicotineCafe.Services.SpeechEngineClient). Reads the catalog straight
    from the shared SQLite database — no JSON editing needed.
    """
    from pathlib import Path
    from server import VoiceEngineServer

    model = args.model_path or args.model
    server = VoiceEngineServer(db_path=Path(args.db), port=args.port, model_size=model)
    server.run()


def mode_explain(args: argparse.Namespace, config: AppConfig) -> None:
    from matcher import ProductMatcher

    matcher = ProductMatcher(config)

    if hasattr(args, "text") and args.text:
        text = args.text
    elif hasattr(args, "file") and args.file:
        from whisper_engine import WhisperEngine
        engine = WhisperEngine(config.whisper)
        engine.load()
        tr = engine.transcribe_file(Path(args.file))
        text = tr.text
        if tr.is_hallucination or not text.strip():
            print("  ⚠ صدا قابل تشخیص نبود")
            return
    else:
        print("  Error: --text or --file required.", file=sys.stderr)
        sys.exit(1)

    print(f"\n  Explaining: {text!r}\n")
    print(matcher.explain(text))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="VoiceBenchmark",
        description="Offline Persian cigarette product voice detector",
        epilog=(
            "Examples:\n"
            "  python main.py mic\n"
            "  python main.py --model tiny mic --loops 5\n"
            "  python main.py explain --text \"ونستون آبی میخوام\"\n"
            "  python main.py file recordings\\rec.wav\n"
            "  python main.py benchmark --models tiny base\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model", choices=ALL_MODEL_SIZES, default="base",
                        help="Whisper model size (default: base)")
    parser.add_argument("--debug", action="store_true")

    sub = parser.add_subparsers(dest="mode", required=True)

    mic_p = sub.add_parser("mic", help="Record from microphone (hold SPACE)")
    mic_p.add_argument("--loops", type=int, default=0,
                       help="Number of recordings — 0 = infinite (default)")

    file_p = sub.add_parser("file", help="Detect from WAV file(s)")
    file_p.add_argument("input", nargs="+", help="WAV file path(s)")

    serve_p = sub.add_parser("serve", help="Run as TCP bridge for the WPF app (production mode)")
    serve_p.add_argument("--port", type=int, default=8765)
    serve_p.add_argument("--db", required=True, help="Path to the shared nicotinecafe.db")
    serve_p.add_argument("--model-path", default=None,
                         help="Path to an already-downloaded faster-whisper model folder "
                              "(overrides --model; use when the machine has no internet access)")

    exp_p = sub.add_parser("explain", help="Full debug trace for text or WAV")
    grp = exp_p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--text", help="Persian text to analyse")
    grp.add_argument("--file", help="WAV file to transcribe and analyse")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = AppConfig(
        whisper=WhisperConfig(model_size=args.model),  # type: ignore[arg-type]
        debug=args.debug,
    ).resolve_paths()

    dispatch = {
        "mic": mode_mic,
        "file": mode_file,
        "serve": mode_serve,
        "explain": mode_explain,
    }
    dispatch[args.mode](args, config)


if __name__ == "__main__":
    main()
    