from __future__ import annotations

import importlib
import re
import sys
import types
from types import SimpleNamespace

from anki_speech_trainer.review_state import ReviewSession, ReviewState


def _load_controller(monkeypatch):
    class FakeQProcess:
        class ProcessState:
            NotRunning = 0
            Running = 1
            Starting = 2

    class FakeEnvironment:
        @staticmethod
        def systemEnvironment():
            return object()

    fake_qt = types.ModuleType("aqt.qt")
    fake_qt.QProcess = FakeQProcess
    fake_qt.QProcessEnvironment = FakeEnvironment
    fake_qt.QTimer = SimpleNamespace(singleShot=lambda _milliseconds, _callback: None)
    fake_aqt = types.ModuleType("aqt")
    fake_anki_utils = types.ModuleType("anki.utils")
    fake_anki_utils.strip_html = lambda value: re.sub(r"<[^>]+>", "", value)
    fake_anki = types.ModuleType("anki")
    monkeypatch.setitem(sys.modules, "aqt", fake_aqt)
    monkeypatch.setitem(sys.modules, "aqt.qt", fake_qt)
    monkeypatch.setitem(sys.modules, "anki", fake_anki)
    monkeypatch.setitem(sys.modules, "anki.utils", fake_anki_utils)
    sys.modules.pop("anki_speech_trainer.controller", None)
    return importlib.import_module("anki_speech_trainer.controller")


def _controller_for_messages(controller_module):
    controller = controller_module.ReviewController.__new__(controller_module.ReviewController)
    controller.session = ReviewSession()
    controller.session.begin_card(7, mapped=True)
    controller.mapping = controller_module.CardMapping("la casa", ())
    controller.process = None
    controller._pending_start = False
    controller._configure_request_id = None
    controller._active_record_request_id = "record-1"
    controller._timed_out_process = None
    controller._shutting_down = False
    controller.rendered = []
    controller._render_status = lambda *args, **kwargs: controller.rendered.append((args, kwargs))
    return controller


def test_controller_discards_a_late_transcript_after_card_change(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    old_session = controller.session.session_id
    controller.session.begin_card(8, mapped=True)

    controller._handle_message(
        SimpleNamespace(
            type="transcript",
            request_id="record-1",
            session_id=old_session,
            payload={"text": "la casa"},
        )
    )

    assert controller.rendered == []
    assert controller.session.state is ReviewState.IDLE


def test_controller_reports_current_transcript_without_an_anki_grade(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)

    controller._handle_message(
        SimpleNamespace(
            type="transcript",
            request_id="record-1",
            session_id=controller.session.session_id,
            payload={"text": "la casa"},
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
            request_id="record-1",
            session_id=controller.session.session_id,
            payload={"code": "microphone_unavailable"},
        )
    )

    assert controller.session.state is ReviewState.ERROR
    assert controller.rendered == [(("error", "Mikrofon nicht verfügbar."), {})]


def test_controller_waits_for_qprocess_started_before_configuring(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    controller._pending_start = True
    sent: list[tuple[str, dict[str, object]]] = []
    controller._send = lambda message_type, payload: sent.append((message_type, payload))
    controller._worker_payload = lambda: {"language": "it"}
    process = SimpleNamespace()
    controller.process = process

    controller._process_started(process)

    assert sent == [("configure", {"language": "it"})]


def test_controller_does_not_write_to_a_starting_qprocess(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    controller.process = SimpleNamespace(state=lambda: module.QProcess.ProcessState.Starting)
    controller._send = lambda *_args: (_ for _ in ()).throw(AssertionError("must wait for started"))
    controller._start_process = lambda: (_ for _ in ()).throw(AssertionError("already starting"))

    controller.start()

    assert controller.session.state is ReviewState.WORKER_STARTING
    assert controller._pending_start


def test_controller_starts_recording_only_for_the_current_configure_reply(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    controller._pending_start = True
    controller._configure_request_id = "configure-current"
    controller._active_record_request_id = None
    sent: list[str] = []
    controller._send = lambda message_type, _payload: sent.append(message_type) or "record-current"

    controller._handle_message(
        SimpleNamespace(
            type="status",
            request_id="configure-current",
            session_id=controller.session.session_id,
            payload={"state": "model_ready"},
        )
    )

    assert sent == ["record_start"]
    assert controller._active_record_request_id == "record-current"


def test_controller_discards_a_late_model_ready_after_cancel(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    controller._pending_start = False
    controller._configure_request_id = None
    sent: list[str] = []
    controller._send = lambda message_type, _payload: sent.append(message_type)

    controller._handle_message(
        SimpleNamespace(
            type="status",
            request_id="configure-cancelled",
            session_id=controller.session.session_id,
            payload={"state": "model_ready"},
        )
    )

    assert sent == []


def test_controller_discards_cancelled_recording_from_same_card(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    controller._active_record_request_id = "record-new"

    controller._handle_message(
        SimpleNamespace(
            type="transcript",
            request_id="record-old",
            session_id=controller.session.session_id,
            payload={"text": "la casa"},
        )
    )

    assert controller.rendered == []
    assert controller._active_record_request_id == "record-new"


def test_cancel_immediately_restores_a_retryable_ui_state(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    controller.process = SimpleNamespace(state=lambda: module.QProcess.ProcessState.NotRunning)
    controller.session.recording()

    controller.cancel_current()

    assert controller.session.state is ReviewState.READY
    assert controller.rendered == [(("ready",), {})]


def test_late_exit_from_an_old_worker_does_not_clear_a_new_worker(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    old_process = SimpleNamespace()
    current_process = SimpleNamespace()
    controller.process = current_process

    controller._process_finished(old_process, 1, object())

    assert controller.process is current_process


def test_timeout_terminates_only_the_active_unresponsive_worker(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    terminated: list[bool] = []
    process = SimpleNamespace(terminate=lambda: terminated.append(True))
    controller.process = process
    controller._configure_request_id = "configure-current"
    controller._active_record_request_id = None

    controller._request_timed_out(process, controller.session.session_id, "configure-current")

    assert terminated == [True]
    assert controller._timed_out_process is process
    assert controller.session.state is ReviewState.ERROR
    assert controller.rendered == [
        (("error", "Sprach-Worker reagiert nicht. Bitte erneut versuchen."), {})
    ]


def test_timeout_ignores_a_replaced_worker_or_request(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    old_process = SimpleNamespace(terminate=lambda: (_ for _ in ()).throw(AssertionError("old")))
    controller.process = SimpleNamespace(
        terminate=lambda: (_ for _ in ()).throw(AssertionError("new"))
    )
    controller._configure_request_id = "configure-new"

    controller._request_timed_out(old_process, controller.session.session_id, "configure-old")

    assert controller.rendered == []


def test_timed_out_worker_exit_keeps_the_timeout_error(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    process = SimpleNamespace()
    controller.process = process
    controller._timed_out_process = process
    controller.session.error()

    controller._process_finished(process, 1, object())

    assert controller.process is None
    assert controller.rendered == []


def test_expected_worker_termination_does_not_render_a_start_error(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    process = SimpleNamespace()
    controller.process = process
    controller._shutting_down = True

    controller._process_error(process, object())

    assert controller.rendered == []


def test_timed_out_worker_termination_does_not_replace_timeout_error(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    process = SimpleNamespace()
    controller.process = process
    controller._timed_out_process = process

    controller._process_error(process, object())

    assert controller.rendered == []


def test_mapping_reads_only_the_configured_note_fields(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    config = {
        "enabled": True,
        "notetype_mappings": [
            {
                "notetype_name": "Italiano A1",
                "answer_field": "Italiano",
                "alternatives_field": "SpeechAlternatives",
            }
        ],
    }
    mw = SimpleNamespace(addonManager=SimpleNamespace(getConfig=lambda _name: config))
    controller = module.ReviewController(mw)

    class Note(dict):
        def note_type(self):
            return {"name": "Italiano A1", "type": 0}

    card = SimpleNamespace(
        note=lambda: Note(
            Italiano="<b>la casa</b> [sound:house.mp3]",
            SpeechAlternatives="casa\n\n",
            Other="must not be read",
        )
    )

    assert controller.mapping_for_card(card) == module.CardMapping("la casa", ("casa",), "it")


def test_mapping_limits_widget_to_named_template_and_uses_mapping_language(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    config = {
        "enabled": True,
        "language": "it",
        "notetype_mappings": [
            {
                "notetype_name": "Italian Practice",
                "card_template_name": "Speaking",
                "language": "it",
                "answer_field": "Target",
                "alternatives_field": "SpokenAlternatives",
            }
        ],
    }
    controller = module.ReviewController(
        SimpleNamespace(addonManager=SimpleNamespace(getConfig=lambda _name: config))
    )

    class Note(dict):
        def note_type(self):
            return {"name": "Italian Practice", "type": 0}

    speaking = SimpleNamespace(
        note=lambda: Note(Target="sono andato", SpokenAlternatives="sono andata"),
        template=lambda: {"name": "Speaking"},
    )
    writing = SimpleNamespace(
        note=lambda: Note(Target="sono andato", SpokenAlternatives="sono andata"),
        template=lambda: {"name": "Writing"},
    )

    assert controller.mapping_for_card(speaking) == module.CardMapping(
        "sono andato", ("sono andata",), "it"
    )
    assert controller.mapping_for_card(writing) is None


def test_legacy_mapping_still_applies_without_a_card_template(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    config = {
        "enabled": True,
        "language": "ru",
        "notetype_mappings": [{"notetype_name": "Russian", "answer_field": "Target"}],
    }
    controller = module.ReviewController(
        SimpleNamespace(addonManager=SimpleNamespace(getConfig=lambda _name: config))
    )

    class Note(dict):
        def note_type(self):
            return {"name": "Russian", "type": 0}

    card = SimpleNamespace(note=lambda: Note(Target="привет"))

    assert controller.mapping_for_card(card) == module.CardMapping("привет", (), "ru")


def test_mapping_rejects_invalid_template_and_language_values(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    config = {
        "enabled": True,
        "notetype_mappings": [
            {
                "notetype_name": "Italian Practice",
                "card_template_name": "Speaking",
                "language": "italian; unsafe",
                "answer_field": "Target",
            }
        ],
    }
    controller = module.ReviewController(
        SimpleNamespace(addonManager=SimpleNamespace(getConfig=lambda _name: config))
    )

    class Note(dict):
        def note_type(self):
            return {"name": "Italian Practice", "type": 0}

    card = SimpleNamespace(
        note=lambda: Note(Target="la casa"), template=lambda: {"name": "Speaking"}
    )

    assert controller.mapping_for_card(card) is None


def test_worker_payload_uses_the_language_of_the_active_mapping(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    controller = _controller_for_messages(module)
    controller.mapping = module.CardMapping("привет", (), "ru")
    controller.config = lambda: {
        "language": "it",
        "model": "base",
        "device": "cpu",
        "compute_type": "int8",
        "microphone_device_id": None,
        "auto_stop_silence_ms": 800,
        "max_record_seconds": 12,
    }

    assert controller._worker_payload()["language"] == "ru"


def test_mapping_excludes_unmapped_and_cloze_notes(monkeypatch) -> None:
    module = _load_controller(monkeypatch)
    config = {
        "enabled": True,
        "notetype_mappings": [{"notetype_name": "Italiano A1", "answer_field": "Italiano"}],
    }
    controller = module.ReviewController(
        SimpleNamespace(addonManager=SimpleNamespace(getConfig=lambda _name: config))
    )

    class Note(dict):
        def __init__(self, note_type):
            super().__init__(Italiano="la casa")
            self._note_type = note_type

        def note_type(self):
            return self._note_type

    assert (
        controller.mapping_for_card(
            SimpleNamespace(note=lambda: Note({"name": "Other", "type": 0}))
        )
        is None
    )
    assert (
        controller.mapping_for_card(
            SimpleNamespace(note=lambda: Note({"name": "Italiano A1", "type": 1}))
        )
        is None
    )
