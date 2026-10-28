from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace

from anki_speech_trainer.review_state import ReviewSession, ReviewState


def _load_controller(monkeypatch):
    class FakeQProcess:
        class ProcessState:
            NotRunning = 0
            Running = 1

    class FakeEnvironment:
        @staticmethod
        def systemEnvironment():
            return object()

    fake_qt = types.ModuleType("aqt.qt")
    fake_qt.QProcess = FakeQProcess
    fake_qt.QProcessEnvironment = FakeEnvironment
    fake_qt.QTimer = SimpleNamespace(singleShot=lambda _milliseconds, _callback: None)
    fake_aqt = types.ModuleType("aqt")
    monkeypatch.setitem(sys.modules, "aqt", fake_aqt)
    monkeypatch.setitem(sys.modules, "aqt.qt", fake_qt)
    sys.modules.pop("anki_speech_trainer.controller", None)
    return importlib.import_module("anki_speech_trainer.controller")


def _controller_for_messages(controller_module):
    controller = controller_module.ReviewController.__new__(controller_module.ReviewController)
    controller.session = ReviewSession()
    controller.session.begin_card(7, mapped=True)
    controller.mapping = controller_module.CardMapping("la casa", ())
    controller._pending_start = False
    controller.rendered = []
    controller._render_status = lambda *args, **kwargs: controller.rendered.append((args, kwargs))
    return controller


def test_controller_discards_a_late_transcript_after_card_change(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    old_session = controller.session.session_id
    controller.session.begin_card(8, mapped=True)

    controller._handle_message(
        SimpleNamespace(type="transcript", session_id=old_session, payload={"text": "la casa"})
    )

    assert controller.rendered == []
    assert controller.session.state is ReviewState.IDLE


def test_controller_reports_current_transcript_without_an_anki_grade(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)

    controller._handle_message(
        SimpleNamespace(
            type="transcript", session_id=controller.session.session_id, payload={"text": "la casa"}
        )
    )

    assert controller.session.state is ReviewState.RESULT
    assert controller.rendered == [(("match",), {"transcript": "la casa"})]


def test_controller_turns_worker_errors_into_a_recoverable_status(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)

    controller._handle_message(
        SimpleNamespace(
            type="error",
            session_id=controller.session.session_id,
            payload={"code": "microphone_unavailable"},
        )
    )

    assert controller.session.state is ReviewState.ERROR
    assert controller.rendered == [(("error", "Mikrofon nicht verfügbar."), {})]
