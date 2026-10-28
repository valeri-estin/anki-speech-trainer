from __future__ import annotations

import sys
import types

import pytest

from anki_speech_trainer.worker.audio import AudioError, capture_speech
from anki_speech_trainer.worker.main import Worker
from anki_speech_trainer.worker.protocol import Message


def test_audio_capture_reports_missing_microphone(monkeypatch) -> None:
    fake_sounddevice = types.SimpleNamespace(query_devices=lambda: [])
    fake_webrtcvad = types.SimpleNamespace(Vad=lambda _aggressiveness: object())
    monkeypatch.setitem(sys.modules, "sounddevice", fake_sounddevice)
    monkeypatch.setitem(sys.modules, "webrtcvad", fake_webrtcvad)

    with pytest.raises(AudioError, match="microphone_unavailable"):
        capture_speech(
            device_id=None,
            silence_ms=800,
            max_seconds=12,
            cancel_event=types.SimpleNamespace(is_set=lambda: False),
        )


def test_worker_rejects_invalid_configuration_without_loading_model() -> None:
    worker = Worker()
    emitted: list[tuple[str, dict[str, object]]] = []
    worker.emit = lambda message_type, _request_id, _session_id, payload: emitted.append(
        (message_type, payload)
    )
    message = Message(1, "configure", "request", "session", {"auto_stop_silence_ms": 801})

    worker.configure(message)

    assert emitted == [("error", {"code": "invalid_configuration"})]


def test_worker_rejects_concurrent_recording() -> None:
    worker = Worker()
    worker._active_cancel = types.SimpleNamespace(set=lambda: None)
    emitted: list[tuple[str, dict[str, object]]] = []
    worker.emit = lambda message_type, _request_id, _session_id, payload: emitted.append(
        (message_type, payload)
    )
    message = Message(1, "record_start", "request", "session", {})

    worker.start_recording(message)

    assert emitted == [("error", {"code": "busy"})]
