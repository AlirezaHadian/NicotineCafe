"""
server.py — TCP bridge between the always-listening Python voice engine and
the WPF app. Protocol: newline-delimited JSON, listening on 127.0.0.1:{port}.
Started by NicotineCafe.Services.VoiceEngineProcessLauncher.

engine -> WPF only (one-way):
  {"type":"audio_level","level":0..1}
  {"type":"recognition", ...}
  {"type":"status","message":"..."}

No push-to-talk, no commands from WPF. AutoVadRecorder listens to the
microphone continuously and calls back automatically the instant it detects
a complete spoken utterance (speech onset -> silence). The customer just
talks — nobody touches a button.
"""
from __future__ import annotations

import argparse
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

from config import AppConfig, WhisperConfig
from matcher import ProductMatcher
from recorder import AutoVadRecorder
from whisper_engine import WhisperEngine


def log(msg: str) -> None:
    ts = __import__("datetime").datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}", flush=True)


def load_engine_settings(db_path: Path) -> dict:
    """
    Read EngineSettings(Key, Value) from the shared SQLite DB — these are
    editable from the WPF admin screen. Returns {} if the table doesn't
    exist yet (older DB) so this never breaks startup.
    """
    import sqlite3
    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT Key, Value FROM EngineSettings").fetchall()
        conn.close()
        return {k: v for k, v in rows}
    except sqlite3.Error:
        return {}


class VoiceEngineServer:
    def __init__(self, db_path: Path, port: int, model_size: str = "tiny") -> None:
        self.port = port
        settings = load_engine_settings(db_path)
        if settings:
            log(f"[VoiceEngineServer] Loaded {len(settings)} setting(s) from EngineSettings table: {settings}")

        # CLI/launcher-provided model_size wins only if the DB doesn't specify one,
        # so the admin screen is the single source of truth once configured.
        effective_model = settings.get("model_size", model_size)
        self.config = AppConfig(whisper=WhisperConfig(model_size=effective_model)).resolve_paths()
        if "beam_size" in settings:
            self.config.whisper.beam_size = int(settings["beam_size"])
        if "min_confidence" in settings:
            self.config.matcher.min_confidence = float(settings["min_confidence"])

        # Pin the faster-whisper model cache to Data/models, next to the
        # shared db, instead of the OS/user-profile default cache location.
        # This guarantees the model is only ever downloaded once per
        # machine/install and reused on every subsequent run, regardless of
        # which Windows user account launches the app or how that profile's
        # cache is configured — this is what was causing it to look like it
        # re-downloads "every time".
        models_dir = db_path.parent / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        self.config.whisper.download_root = str(models_dir)

        log(f"[VoiceEngineServer] Loading brand catalog from {db_path} ...")
        self.matcher = ProductMatcher.from_sqlite(db_path, self.config)
        log(f"[VoiceEngineServer] Catalog loaded: {len(self.matcher.available_brands)} brands.")

        self.engine = WhisperEngine(self.config.whisper)
        if "cpu_threads" in settings:
            self.engine.cpu_threads = int(settings["cpu_threads"])

        # Always-listening VAD recorder: no button, no start/stop commands.
        # As soon as it detects speech -> silence, it hands the audio to
        # _on_utterance() automatically.
        self.recorder = AutoVadRecorder(
            self.config.recorder,
            utterance_callback=self._on_utterance,
            level_callback=self._send_audio_level,
            speech_threshold=float(settings.get("speech_threshold", 0.09)),
            silence_hangover_s=float(settings.get("silence_hangover_s", 0.55)),
            min_utterance_s=float(settings.get("min_utterance_s", 0.9)),
        )

        self._conn: socket.socket | None = None
        self._conn_lock = threading.Lock()
        self._process_lock = threading.Lock()  # serializes Whisper calls; VAD tracking is unaffected

    # ------------------------------------------------------------------
    # Outbound messages
    # ------------------------------------------------------------------

    def _send(self, payload: dict) -> None:
        with self._conn_lock:
            if self._conn is None:
                return
            try:
                self._conn.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
            except OSError as ex:
                log(f"[VoiceEngineServer] send failed, dropping connection: {ex!r}")
                self._conn = None

    def _send_audio_level(self, level: float) -> None:
        self._send({"type": "audio_level", "level": round(level, 3)})

    def _send_recognition(self, result) -> None:
        payload = {
            "type": "recognition",
            "isValid": result.is_valid,
            "brandId": result.brand_id,
            "rawText": result.raw_text,
            "normalisedText": result.normalised_text,
            "confidence": round(result.confidence, 4),
            "debugBrand": result.brand_match.brand,
            "debugBrandScore": round(result.brand_match.score, 1),
        }
        log(f"[VoiceEngineServer] recognition: {payload}")
        self._send(payload)

    def _send_status(self, message: str) -> None:
        self._send({"type": "status", "message": message})

    def _dispatch_client_message(self, line: str) -> None:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            return
        msg_type = msg.get("type")
        if msg_type == "pause":
            self.recorder.pause()
            log("[VoiceEngineServer] listening PAUSED by operator")
            self._send_status("paused")
        elif msg_type == "resume":
            self.recorder.resume()
            log("[VoiceEngineServer] listening RESUMED by operator")
            self._send_status("resumed")

    # ------------------------------------------------------------------
    # Called automatically by AutoVadRecorder whenever it captures a
    # complete utterance (speech onset -> silence). No commands from
    # the WPF app are involved at all.
    # ------------------------------------------------------------------

    def _on_utterance(self, audio) -> None:
        with self._process_lock:
            self._process_utterance(audio)

    def _process_utterance(self, audio) -> None:
        t_start = time.perf_counter()
        self._send_status("processing")

        transcription = self.engine.transcribe(audio)
        t_transcribe_end = time.perf_counter()
        duration_s = len(audio) / self.config.recorder.sample_rate
        log(f"[VoiceEngineServer] TIMING: audio={duration_s:.2f}s, "
            f"transcribe={t_transcribe_end - t_start:.2f}s")

        if transcription.is_hallucination or not transcription.text.strip():
            self._send_status("no_speech_detected")
            return

        t_match_start = time.perf_counter()
        result = self.matcher.match(transcription.text)
        t_match_end = time.perf_counter()
        log(f"[VoiceEngineServer] TIMING: match={t_match_end - t_match_start:.3f}s, "
            f"TOTAL utterance->result={t_match_end - t_start:.2f}s")

        # Best-effort logging for continuous accuracy improvement — review
        # invalid/low-confidence rows periodically and add real phrases as
        # aliases (see RecognitionLog table).
        if self.matcher.catalog is not None:
            self.matcher.catalog.log_recognition(
                raw_text=result.raw_text,
                normalised_text=result.normalised_text,
                brand_id=result.brand_id,
                confidence=result.confidence,
                is_valid=result.is_valid,
            )

        self._send_recognition(result)

    # ------------------------------------------------------------------
    # TCP accept loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        # Bind/listen FIRST — the WPF client can connect right away (it
        # retries on a short interval) instead of waiting for the model to
        # finish loading/downloading before the socket even exists. This is
        # what lets the WPF side show a real "loading" state instead of
        # just looking disconnected/frozen for however long the model load
        # takes (which can be minutes on a first run that has to download).
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

            model_ready = False

            while True:
                conn, _addr = listener.accept()
                with self._conn_lock:
                    self._conn = conn
                log("[VoiceEngineServer] WPF client connected")

                if not model_ready:
                    self._send_status("loading_model")
                    log("[VoiceEngineServer] Loading Whisper model (first run downloads it — needs internet once) ...")
                    load_time = self.engine.load()
                    log(f"[VoiceEngineServer] Whisper model loaded in {load_time:.2f}s.")

                    self.recorder.start()
                    log("[VoiceEngineServer] Microphone is now listening continuously (VAD auto-trigger).")
                    model_ready = True

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
                log("[VoiceEngineServer] WPF client disconnected")


def main() -> None:
    parser = argparse.ArgumentParser(description="Nicotine Cafe voice engine — TCP bridge server")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", required=True, help="Path to the shared nicotinecafe.db")
    parser.add_argument("--model", default="tiny", choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"])
    args = parser.parse_args()

    try:
        server = VoiceEngineServer(db_path=Path(args.db), port=args.port, model_size=args.model)
        server.run()
    except Exception as ex:  # last-resort visibility into the log file
        log(f"[VoiceEngineServer] FATAL: {ex!r}")
        raise


if __name__ == "__main__":
    main()
