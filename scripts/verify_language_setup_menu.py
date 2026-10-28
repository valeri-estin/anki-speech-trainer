#!/usr/bin/env python3
"""Smoke-test the Tools-menu entry with Anki's bundled Qt runtime."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    from aqt.qt import QApplication, QMainWindow, QMenu

    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    tools_menu = QMenu(window)
    mw = SimpleNamespace(form=SimpleNamespace(menuTools=tools_menu))
    from anki_speech_trainer.language_setup_dialog import install_language_setup_menu

    action = install_language_setup_menu(mw, "anki_speech_trainer")
    submenu = action.parent()
    if not isinstance(submenu, QMenu) or submenu.title() != "Anki Speech Trainer":
        print("missing_submenu", file=sys.stderr)
        return 1
    if action.text() != "Sprach-Deck einrichten…" or action not in submenu.actions():
        print("missing_setup_action", file=sys.stderr)
        return 1
    if not any(menu_action.menu() is submenu for menu_action in tools_menu.actions()):
        print("submenu_not_added_to_tools", file=sys.stderr)
        return 1
    app.processEvents()
    print("Language setup menu is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
