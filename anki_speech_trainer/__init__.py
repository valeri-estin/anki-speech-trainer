"""Local speech-practice integration for Anki's reviewer.

This package intentionally imports only Anki's bundled runtime. Audio and ML
dependencies live in the separately started worker process.
"""

from __future__ import annotations


class AnkiSpeechTrainer:
    """Wire public Anki hooks to the isolated speech-practice controller."""

    def __init__(self) -> None:
        from aqt import gui_hooks, mw

        from .controller import ReviewController
        from .review_ui import ReviewUi

        self.controller = ReviewController(mw)
        self.ui = ReviewUi(self.controller)
        gui_hooks.card_will_show.append(self.ui.card_will_show)
        gui_hooks.reviewer_did_show_question.append(self.controller.did_show_question)
        gui_hooks.reviewer_did_show_answer.append(self.controller.did_show_answer)
        gui_hooks.webview_did_receive_js_message.append(self.ui.receive_js_message)
        gui_hooks.profile_will_close.append(self.controller.shutdown)


try:
    import aqt as _aqt  # The external worker must be able to import its subpackage without Anki.
except ImportError:  # pragma: no cover - exercised by worker's isolated interpreter
    pass
else:
    del _aqt
    addon = AnkiSpeechTrainer()
