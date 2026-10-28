from __future__ import annotations

from anki_speech_trainer.review_ui import _WIDGET


def test_widget_renders_transcript_with_textcontent_not_html() -> None:
    assert "result.textContent" in _WIDGET
    assert "result.innerHTML" not in _WIDGET
    assert "anki_speech_trainer:" in _WIDGET


def test_widget_does_not_expose_expected_answer() -> None:
    assert "Erwartet:" not in _WIDGET
