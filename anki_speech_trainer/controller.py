"""Non-blocking reviewer controller backed by Anki's QProcess."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aqt.qt import QProcess, QProcessEnvironment, QTimer

from .matching import Comparison, compare
from .review_state import ReviewSession, ReviewState
from .worker.protocol import RESPONSE_TYPES, LineBuffer, ProtocolError, decode_line, encode

_SOUND_TAG = re.compile(r"\[sound:[^\]]+\]", re.IGNORECASE)


@dataclass(frozen=True)
class CardMapping:
    expected: str
    alternatives: tuple[str, ...]


class ReviewController:
    """The sole owner of visible widget state and worker requests."""

    def __init__(self, mw: Any) -> None:
        self.mw = mw
        self.session = ReviewSession()
        self.mapping: CardMapping | None = None
        self.process: QProcess | None = None
        self._buffer = LineBuffer()
        self._request_counter = 0
        self._pending_start = False
        self._shutting_down = False

    def config(self) -> dict[str, Any]:
        config = self.mw.addonManager.getConfig(__package__) or {}
        return config if isinstance(config, dict) else {}

    def mapping_for_card(self, card: Any) -> CardMapping | None:
        config = self.config()
        if not config.get("enabled", True):
            return None
        note = card.note()
        note_type = note.note_type()
        if note_type.get("type") == 1:  # Cloze target extraction is intentionally unsupported.
            return None
        note_type_name = note_type.get("name")
        for raw_mapping in config.get("notetype_mappings", []):
            if (
                not isinstance(raw_mapping, dict)
                or raw_mapping.get("notetype_name") != note_type_name
            ):
                continue
            answer_field = raw_mapping.get("answer_field")
            alternatives_field = raw_mapping.get("alternatives_field")
            if not isinstance(answer_field, str) or answer_field not in note:
                return None
            expected = self._plaintext(note[answer_field])
            alternatives: tuple[str, ...] = ()
            if isinstance(alternatives_field, str) and alternatives_field in note:
                alternatives = tuple(
                    value
                    for value in (
                        self._plaintext(line) for line in note[alternatives_field].splitlines()
                    )
                    if value
                )
            return CardMapping(expected=expected, alternatives=alternatives) if expected else None
        return None

    @staticmethod
    def _plaintext(value: str) -> str:
        from anki.utils import strip_html

        return _SOUND_TAG.sub("", strip_html(value)).strip()

    def did_show_question(self, card: Any) -> None:
        self.cancel_current()
        self.mapping = self.mapping_for_card(card)
        self.session.begin_card(card.id, self.mapping is not None)
        self._pending_start = False

    def did_show_answer(self, _card: Any) -> None:
        self.cancel_current()

    def handle_action(self, action: str) -> bool:
        if not self.session.mapped:
            return False
        if action == "start":
            self.start()
            return True
        if action in {"stop", "cancel"}:
            self.cancel_current()
            return True
        return False

    def start(self) -> None:
        if self.session.state in {
            ReviewState.WORKER_STARTING,
            ReviewState.RECORDING,
            ReviewState.TRANSCRIBING,
        }:
            return
        self._pending_start = True
        if self.process is None or self.process.state() == QProcess.ProcessState.NotRunning:
            if not self._start_process():
                return
        self.session.start_worker()
        self._render_status("worker_starting")
        self._send("configure", self._worker_payload())

    def _start_process(self) -> bool:
        worker_python = self.config().get("worker_python")
        if (
            not isinstance(worker_python, str)
            or not Path(worker_python).is_absolute()
            or not Path(worker_python).is_file()
        ):
            self.session.error()
            self._render_status("error", "Worker-Python ist nicht konfiguriert.")
            return False
        worker_script = Path(__file__).resolve().parent / "worker" / "main.py"
        process = QProcess(self.mw)
        process.setProcessEnvironment(QProcessEnvironment.systemEnvironment())
        process.readyReadStandardOutput.connect(self._read_stdout)
        process.readyReadStandardError.connect(self._read_stderr)
        process.errorOccurred.connect(self._process_error)
        process.finished.connect(self._process_finished)
        process.start(worker_python, [str(worker_script)])
        self.process = process
        return True

    def _worker_payload(self) -> dict[str, Any]:
        config = self.config()
        return {
            "language": config.get("language", "it"),
            "model": config.get("model", "base"),
            "device": config.get("device", "cpu"),
            "compute_type": config.get("compute_type", "int8"),
            "microphone_device_id": config.get("microphone_device_id"),
            "auto_stop_silence_ms": config.get("auto_stop_silence_ms", 800),
            "max_record_seconds": config.get("max_record_seconds", 12),
        }

    def _send(self, message_type: str, payload: dict[str, Any]) -> str | None:
        if self.process is None or self.process.state() != QProcess.ProcessState.Running:
            self.session.error()
            self._render_status("error", "Sprach-Worker ist nicht verfügbar.")
            return None
        self._request_counter += 1
        request_id = f"request-{self._request_counter}"
        self.process.write(encode(message_type, request_id, self.session.session_id, payload))
        return request_id

    def _read_stdout(self) -> None:
        if self.process is None:
            return
        try:
            lines = self._buffer.feed(bytes(self.process.readAllStandardOutput()))
            for line in lines:
                self._handle_message(decode_line(line, allowed_types=RESPONSE_TYPES))
        except ProtocolError:
            self.session.error()
            self._render_status("error", "Ungültige Antwort des Sprach-Workers.")

    def _read_stderr(self) -> None:
        if self.process is None:
            return
        # Diagnostics are not displayed or persisted because they may contain device details.
        self.process.readAllStandardError()

    def _handle_message(self, message: Any) -> None:
        if not self.session.accepts(message.session_id):
            return
        if message.type == "status":
            state = message.payload.get("state")
            if state == "model_ready":
                self.session.worker_ready()
                if self._pending_start:
                    self._pending_start = False
                    self._send("record_start", {})
                return
            if state == "recording":
                self.session.recording()
                self._render_status("recording")
            elif state == "transcribing":
                self.session.transcribing()
                self._render_status("transcribing")
            return
        if message.type == "transcript":
            self._handle_transcript(message.payload)
            return
        if message.type == "cancelled":
            self.session.cancel()
            self._render_status("ready")
            return
        if message.type == "error":
            self.session.error()
            self._render_status("error", self._error_text(message.payload.get("code")))

    def _handle_transcript(self, payload: dict[str, Any]) -> None:
        if self.mapping is None:
            return
        text = payload.get("text")
        comparison: Comparison = compare(
            text if isinstance(text, str) else "", self.mapping.expected, self.mapping.alternatives
        )
        if comparison.status == "uncertain":
            self.session.result()
            self._render_status("uncertain")
            return
        self.session.result()
        self._render_status(comparison.status, transcript=text if isinstance(text, str) else "")

    @staticmethod
    def _error_text(code: object) -> str:
        messages = {
            "microphone_unavailable": "Mikrofon nicht verfügbar.",
            "no_speech": "Nicht sicher erkannt. Bitte erneut versuchen.",
            "model_unavailable": "Sprachmodell nicht verfügbar.",
            "busy": "Eine Aufnahme läuft bereits.",
        }
        return messages.get(code, "Spracherkennung ist derzeit nicht verfügbar.")

    def cancel_current(self) -> None:
        self._pending_start = False
        if self.process is not None and self.process.state() == QProcess.ProcessState.Running:
            self._send("record_cancel", {})
        self.session.cancel()

    def _process_error(self, _error: Any) -> None:
        if self.session.mapped:
            self.session.error()
            self._render_status("error", "Sprach-Worker konnte nicht gestartet werden.")

    def _process_finished(self, _exit_code: int, _status: Any) -> None:
        self.process = None
        if (
            not self._shutting_down
            and self.session.mapped
            and self.session.state not in {ReviewState.IDLE, ReviewState.READY}
        ):
            self.session.error()
            self._render_status("error", "Sprach-Worker wurde beendet.")

    def _render_status(
        self, state: str, message: str | None = None, transcript: str | None = None
    ) -> None:
        payload = json.dumps(
            {"state": state, "message": message, "transcript": transcript}, ensure_ascii=False
        )
        reviewer = getattr(self.mw, "reviewer", None)
        if reviewer is not None:
            reviewer.web.eval(
                f"window.AnkiSpeechTrainer && window.AnkiSpeechTrainer.update({payload});"
            )

    def shutdown(self) -> None:
        self._shutting_down = True
        self.cancel_current()
        if self.process is not None and self.process.state() == QProcess.ProcessState.Running:
            self._send("shutdown", {})
            process = self.process
            QTimer.singleShot(2_000, lambda: self._terminate_if_running(process))

    @staticmethod
    def _terminate_if_running(process: QProcess) -> None:
        if process.state() != QProcess.ProcessState.NotRunning:
            process.terminate()

    def profile_opened(self) -> None:
        self._shutting_down = False
        self.process = None
        self.mapping = None
        self.session = ReviewSession()
