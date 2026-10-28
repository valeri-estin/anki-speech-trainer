from __future__ import annotations

import sys
import threading
import types

import pytest

from anki_speech_trainer.worker.audio import AudioError, capture_speech
from anki_speech_trainer.worker.main import Worker
from anki_speech_trainer.worker.protocol import Message
from anki_speech_trainer.worker.transcriber import LocalTranscriber, TranscriptionError


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


def test_audio_capture_keeps_preroll_and_stops_after_vad_silence(monkeypatch) -> None:
    silence = b"\x00" * 640
    speech = b"\x01" * 640

    class Stream:
        def __init__(self) -> None:
            self.frames = iter([silence, silence, speech, silence, silence])

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _samples: int):
            return next(self.frames), False

    class Vad:
        def __init__(self, _aggressiveness: int) -> None:
            pass

        def is_speech(self, frame: bytes, _sample_rate: int) -> bool:
            return frame == speech

    fake_sounddevice = types.SimpleNamespace(
        query_devices=lambda: [{"max_input_channels": 1}], RawInputStream=lambda **_kwargs: Stream()
    )
    monkeypatch.setitem(sys.modules, "sounddevice", fake_sounddevice)
    monkeypatch.setitem(sys.modules, "webrtcvad", types.SimpleNamespace(Vad=Vad))

    audio = capture_speech(
        device_id=None,
        silence_ms=40,
        max_seconds=12,
        cancel_event=threading.Event(),
    )

    assert audio.duration_ms == 100
    assert audio.pcm == silence + silence + speech + silence + silence


def test_audio_capture_honors_cancellation_before_reading(monkeypatch) -> None:
    class Stream:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _samples: int):
            raise AssertionError("must not read after cancellation")

    fake_sounddevice = types.SimpleNamespace(
        query_devices=lambda: [{"max_input_channels": 1}],
        RawInputStream=lambda **_kwargs: Stream(),
    )
    monkeypatch.setitem(sys.modules, "sounddevice", fake_sounddevice)
    monkeypatch.setitem(
        sys.modules, "webrtcvad", types.SimpleNamespace(Vad=lambda _value: object())
    )
    cancelled = threading.Event()
    cancelled.set()

    with pytest.raises(AudioError, match="cancelled"):
        capture_speech(
            device_id=None,
            silence_ms=800,
            max_seconds=12,
            cancel_event=cancelled,
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


def test_transcriber_rejects_an_oversized_worker_response() -> None:
    transcriber = LocalTranscriber()
    transcriber._model = types.SimpleNamespace(
        transcribe=lambda *_args, **_kwargs: ([types.SimpleNamespace(text="x" * 4_097)], object())
    )
    audio = types.SimpleNamespace(pcm=b"\x00\x00" * 320)

    with pytest.raises(TranscriptionError, match="transcript_too_long"):
        transcriber.transcribe(audio, language="it")
