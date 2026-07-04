"""
server.py — TCP loopback bridge between the Python voice engine and the
WPF app. Protocol: newline-delimited JSON, listening on 127.0.0.1:{port}.
Started by NicotineCafe.Services.VoiceEngineProcessLauncher.

Bidirectional:
  WPF  -> engine : {"type":"start_recording"} / {"type":"stop_recording"}
  engine -> WPF  : {"type":"audio_level","level":0..1}
                   {"type":"recognition", ...}
                   {"type":"status","message":"..."}

No global keyboard hook (the old SPACE-bar trigger needed Administrator
rights on Windows and failed silently without it). Recording is now
driven entirely by explicit commands from the WPF UI — e.g. a
push-to-talk button or mic icon.
"""
from __future__ import annotations

import argparse
import io
import json
import socket
import sys
import threading
import time
from pathlib import Path

# On Windows, when stdout/stderr are redirected (as WPF does), Python falls
# back to the console's legacy code page (cp1252) instead of UTF-8 — any
# Persian text in a print()/log() call then crashes with UnicodeEncodeError.
# Force UTF-8 explicitly, with a safe fallback instead of crashing.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

# Windows consoles default to a legacy codepage (cp1252) that cannot encode
# Persian text. Force UTF-8 on stdout/stderr so logging Persian product
# names/utterances never crashes the process (this was the cause of the
# "exited early with code 1" crash right after a successful recognition).
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from config import AppConfig, WhisperConfig
from matcher import ProductMatcher
from recorder import ControlledRecorder
from whisper_engine import WhisperEngine


def log(msg: str) -> None:
    ts = __import__("datetime").datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}", flush=True)


class VoiceEngineServer:
    def __init__(self, db_path: Path, port: int, model_size: str = "base") -> None:
        self.port = port
        self.config = AppConfig(whisper=WhisperConfig(model_size=model_size)).resolve_paths()

        log(f"[VoiceEngineServer] Loading product catalog from {db_path} ...")
        self.matcher = ProductMatcher.from_sqlite(db_path, self.config)
        log(f"[VoiceEngineServer] Catalog loaded: "
            f"{len(self.matcher.available_brands)} brands, "
            f"{len(self.matcher.available_variants)} variants.")

        self.engine = WhisperEngine(self.config.whisper)
        self.recorder = ControlledRecorder(self.config.recorder, level_callback=self._send_audio_level)

        self._conn: socket.socket | None = None
        self._conn_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Outbound messages
    # ------------------------------------------------------------------

    def _send(self, payload: dict) -> None:
        log(f"[VoiceEngineServer] -> sending to WPF: {payload}")
        with self._conn_lock:
            if self._conn is None:
                log("[VoiceEngineServer] (no client connected — message dropped)")
                return
            try:
                self._conn.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
            except OSError as ex:
                log(f"[VoiceEngineServer] send failed, dropping connection: {ex!r}")
                self._conn = None

    def _send_audio_level(self, level: float) -> None:
        self._send({"type": "audio_level", "level": round(level, 3)})

    def _send_recognition(self, result) -> None:
        self._send({
            "type": "recognition",
            "isValid": result.is_valid,
            "productId": result.product_id,
            "rawText": result.raw_text,
            "normalisedText": result.normalised_text,
            "confidence": round(result.product.confidence, 4),
            # Debug-only fields (ignored by the WPF DTO, visible here in the log):
            "debugBrand": result.brand_match.brand,
            "debugBrandScore": round(result.brand_match.score, 1),
            "debugVariant": result.variant_match.variant,
            "debugVariantScore": round(result.variant_match.score, 1),
        })

    def _send_status(self, message: str) -> None:
        log(f"[VoiceEngineServer] status: {message}")
        self._send({"type": "status", "message": message})

    # ------------------------------------------------------------------
    # Recording control (called from the client-message loop)
    # ------------------------------------------------------------------

    def _handle_start_recording(self) -> None:
        if self.recorder.is_recording:
            return
        self.recorder.start()
        self._send_status("recording_started")

    def _handle_stop_recording(self) -> None:
        if not self.recorder.is_recording:
            return
        t_stop = time.perf_counter()
        audio = self.recorder.stop()
        self._send_status("recording_stopped")

        if audio is None or audio.size == 0:
            self._send_status("no_audio_captured")
            return

        duration_s = len(audio) / self.config.recorder.sample_rate
        if duration_s < self.config.recorder.min_duration_s:
            self._send_status("recording_too_short")
            return

        t_transcribe_start = time.perf_counter()
        transcription = self.engine.transcribe(audio)
        t_transcribe_end = time.perf_counter()
        log(f"[VoiceEngineServer] TIMING: audio={duration_s:.2f}s, "
            f"stop->transcribe_start={t_transcribe_start - t_stop:.2f}s, "
            f"transcribe={t_transcribe_end - t_transcribe_start:.2f}s")

        if transcription.is_hallucination or not transcription.text.strip():
            self._send_status("no_speech_detected")
            return

        t_match_start = time.perf_counter()
        result = self.matcher.match(transcription.text)
        t_match_end = time.perf_counter()
        log(f"[VoiceEngineServer] TIMING: match={t_match_end - t_match_start:.3f}s, "
            f"TOTAL stop->result={t_match_end - t_stop:.2f}s")
        self._send_recognition(result)

    def _dispatch_client_message(self, line: str) -> None:
        log(f"[VoiceEngineServer] <- received from WPF: {line}")
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            log(f"[VoiceEngineServer] could not parse as JSON, ignoring: {line!r}")
            return
        msg_type = msg.get("type")
        if msg_type == "start_recording":
            self._handle_start_recording()
        elif msg_type == "stop_recording":
            self._handle_stop_recording()
        else:
            log(f"[VoiceEngineServer] unknown message type: {msg_type!r}")

    # ------------------------------------------------------------------
    # TCP accept loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        log("[VoiceEngineServer] Loading Whisper model (first run downloads it — needs internet once) ...")
        load_time = self.engine.load()
        log(f"[VoiceEngineServer] Whisper model loaded in {load_time:.2f}s.")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                listener.bind(("127.0.0.1", self.port))
            except OSError as ex:
                log(f"[VoiceEngineServer] FATAL: could not bind 127.0.0.1:{self.port} — {ex}")
                log("[VoiceEngineServer] This almost always means an OLD python.exe from a previous "
                    "run is still alive and holding the port. Open Task Manager, end every "
                    "'python.exe' / 'main.py' process, then run again.")
                sys.exit(1)
            listener.listen(1)
            log(f"[VoiceEngineServer] listening on 127.0.0.1:{self.port}")

            while True:
                conn, _addr = listener.accept()
                with self._conn_lock:
                    self._conn = conn
                log("[VoiceEngineServer] WPF client connected")
                self._send_status("engine_ready")

                try:
                    buf = b""
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        buf += chunk
                        while b"\n" in buf:
                            line, buf = buf.split(b"\n", 1)
                            if line.strip():
                                self._dispatch_client_message(line.decode("utf-8", errors="ignore"))
                except OSError:
                    pass

                with self._conn_lock:
                    self._conn = None
                if self.recorder.is_recording:
                    self.recorder.stop()
                log("[VoiceEngineServer] WPF client disconnected")


def main() -> None:
    parser = argparse.ArgumentParser(description="Nicotine Cafe voice engine — TCP bridge server")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", required=True, help="Path to the shared nicotinecafe.db")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small"],
                         help="Named model size to auto-download/cache (ignored if --model-path is set)")
    parser.add_argument("--model-path", default=None,
                         help="Path to an already-downloaded faster-whisper/CTranslate2 model folder "
                              "(use this if the machine has no internet access)")
    args = parser.parse_args()

    try:
        server = VoiceEngineServer(
            db_path=Path(args.db), port=args.port,
            model_size=args.model_path or args.model,
        )
        server.run()
    except Exception as ex:  # last-resort visibility into the log file
        log(f"[VoiceEngineServer] FATAL: {ex!r}")
        raise


if __name__ == "__main__":
    main()
