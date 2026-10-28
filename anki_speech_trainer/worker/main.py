"""JSONL worker entry point. Stdout is reserved exclusively for protocol messages."""

from __future__ import annotations

import sys
import threading
from dataclasses import dataclass
from typing import Any

try:  # Supports direct execution by QProcess and package execution in tests.
    from audio import AudioError, capture_speech
    from protocol import REQUEST_TYPES, Message, ProtocolError, decode_line, encode
    from transcriber import LocalTranscriber, TranscriptionError
except ImportError:  # pragma: no cover - exercised by package imports
    from .audio import AudioError, capture_speech
    from .protocol import REQUEST_TYPES, Message, ProtocolError, decode_line, encode
    from .transcriber import LocalTranscriber, TranscriptionError


@dataclass(frozen=True)
class WorkerConfig:
    language: str = "it"
    model: str = "base"
    device: str = "cpu"
    compute_type: str = "int8"
    microphone_device_id: int | None = None
    auto_stop_silence_ms: int = 800
    max_record_seconds: int = 12


class Worker:
    """Serializes model use while allowing stdin cancellation during capture."""

    def __init__(self) -> None:
        self.config = WorkerConfig()
        self.transcriber = LocalTranscriber()
        self._emit_lock = threading.Lock()
        self._active_cancel: threading.Event | None = None
        self._active_request_id: str | None = None

    def emit(
        self, message_type: str, request_id: str, session_id: str, payload: dict[str, Any]
    ) -> None:
        with self._emit_lock:
            sys.stdout.buffer.write(encode(message_type, request_id, session_id, payload))
            sys.stdout.buffer.flush()

    def error(self, message: Message, code: str) -> None:
        self.emit("error", message.request_id, message.session_id, {"code": code})

    def configure(self, message: Message) -> None:
        payload = message.payload
        try:
            microphone_device_id = payload.get("microphone_device_id")
            if microphone_device_id is not None and (
                not isinstance(microphone_device_id, int) or microphone_device_id < 0
            ):
                raise ValueError
            config = WorkerConfig(
                language=_bounded_string(payload.get("language", "it"), 2, 12),
                model=_bounded_string(payload.get("model", "base"), 1, 512),
                device=_bounded_string(payload.get("device", "cpu"), 1, 32),
                compute_type=_bounded_string(payload.get("compute_type", "int8"), 1, 32),
                microphone_device_id=microphone_device_id,
                auto_stop_silence_ms=_bounded_int(
                    payload.get("auto_stop_silence_ms", 800), 20, 3_000
                ),
                max_record_seconds=_bounded_int(payload.get("max_record_seconds", 12), 1, 60),
            )
            if config.auto_stop_silence_ms % 20:
                raise ValueError
        except ValueError:
            self.error(message, "invalid_configuration")
            return
        self.config = config
        self.emit("status", message.request_id, message.session_id, {"state": "initializing"})
        try:
            model_load_ms = self.transcriber.configure(
                model=config.model, device=config.device, compute_type=config.compute_type
            )
        except TranscriptionError as exc:
            self.error(message, str(exc))
            return
        self.emit(
            "status",
            message.request_id,
            message.session_id,
            {"state": "model_ready", "model_load_ms": model_load_ms},
        )

    def start_recording(self, message: Message) -> None:
        if self._active_cancel is not None:
            self.error(message, "busy")
            return
        self._active_cancel = threading.Event()
        self._active_request_id = message.request_id
        threading.Thread(
            target=self._record, args=(message, self._active_cancel), daemon=True
        ).start()

    def _record(self, message: Message, cancel_event: threading.Event) -> None:
        try:
            self.emit("status", message.request_id, message.session_id, {"state": "recording"})
            audio = capture_speech(
                device_id=self.config.microphone_device_id,
                silence_ms=self.config.auto_stop_silence_ms,
                max_seconds=self.config.max_record_seconds,
                cancel_event=cancel_event,
            )
            if cancel_event.is_set():
                self.emit("cancelled", message.request_id, message.session_id, {})
                return
            self.emit("status", message.request_id, message.session_id, {"state": "transcribing"})
            transcript = self.transcriber.transcribe(audio, language=self.config.language)
            if cancel_event.is_set():
                self.emit("cancelled", message.request_id, message.session_id, {})
                return
            self.emit(
                "transcript",
                message.request_id,
                message.session_id,
                {
                    "text": transcript.text,
                    "language": self.config.language,
                    "duration_ms": audio.duration_ms,
                    "transcription_ms": transcript.duration_ms,
                },
            )
        except AudioError as exc:
            if str(exc) == "cancelled":
                self.emit("cancelled", message.request_id, message.session_id, {})
            else:
                self.error(message, str(exc))
        except TranscriptionError as exc:
            self.error(message, str(exc))
        finally:
            self._active_cancel = None
            self._active_request_id = None

    def cancel(self, message: Message) -> None:
        if self._active_cancel is not None:
            self._active_cancel.set()
        self.emit("cancelled", message.request_id, message.session_id, {})

    def handle(self, message: Message) -> bool:
        if message.type == "configure":
            self.configure(message)
        elif message.type == "record_start":
            self.start_recording(message)
        elif message.type in {"record_stop", "record_cancel"}:
            self.cancel(message)
        elif message.type == "shutdown":
            self.cancel(message)
            return False
        return True


def _bounded_string(value: object, minimum: int, maximum: int) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ValueError
    return value


def _bounded_int(value: object, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError
    return value


def main() -> int:
    worker = Worker()
    for raw_line in sys.stdin.buffer:
        try:
            message = decode_line(raw_line.rstrip(b"\n"), allowed_types=REQUEST_TYPES)
        except ProtocolError as exc:
            print(f"Invalid worker protocol input: {exc}", file=sys.stderr)
            continue
        if not worker.handle(message):
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
