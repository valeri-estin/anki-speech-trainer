"""Qt dialog for the explicitly confirmed language-practice setup action."""

from __future__ import annotations

from typing import Any

from aqt.qt import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from .language_setup import LanguageSetupError, apply_language_setup, plan_language_setup

_LANGUAGES = (
    ("Russisch", "ru"),
    ("Französisch", "fr"),
    ("Spanisch", "es"),
    ("Englisch", "en"),
    ("Deutsch", "de"),
    ("Portugiesisch", "pt"),
    ("Polnisch", "pl"),
    ("Niederländisch", "nl"),
    ("Ukrainisch", "uk"),
    ("Türkisch", "tr"),
    ("Japanisch", "ja"),
    ("Koreanisch", "ko"),
    ("Chinesisch", "zh"),
)
_CUSTOM_INDEX = len(_LANGUAGES)


class LanguageSetupDialog(QDialog):
    """Preview collection changes, then create one isolated language setup."""

    def __init__(self, mw: Any, addon_package: str) -> None:
        super().__init__(mw)
        self.mw = mw
        self.addon_package = addon_package
        self.setWindowTitle("Sprach-Deck einrichten")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        explanation = QLabel(
            "Erstellt nach Bestätigung einen neuen Notiztyp, vier Unterdecks und eine "
            "Speaking-Zuordnung. Bestehende Karten, Decks und Einstellungen bleiben unverändert."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        form = QFormLayout()
        self.language_choice = QComboBox(self)
        for name, code in _LANGUAGES:
            self.language_choice.addItem(f"{name} ({code})", (name, code))
        self.language_choice.addItem("Andere Sprache …", None)
        self.name_input = QLineEdit(self)
        self.code_input = QLineEdit(self)
        self.code_input.setMaxLength(3)
        form.addRow("Sprache:", self.language_choice)
        form.addRow("Deck- und Notiztypname:", self.name_input)
        form.addRow("Whisper-Sprachcode:", self.code_input)
        layout.addLayout(form)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok,
            parent=self,
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Vorschau anzeigen")
        self.buttons.accepted.connect(self._preview_and_apply)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.language_choice.currentIndexChanged.connect(self._update_inputs)
        self._update_inputs()

    def _update_inputs(self) -> None:
        selected = self.language_choice.currentData()
        custom = self.language_choice.currentIndex() == _CUSTOM_INDEX
        self.name_input.setReadOnly(not custom)
        self.code_input.setReadOnly(not custom)
        if selected is None:
            self.name_input.clear()
            self.code_input.clear()
            return
        name, code = selected
        self.name_input.setText(name)
        self.code_input.setText(code)

    def _preview_and_apply(self) -> None:
        collection = getattr(self.mw, "col", None)
        if collection is None:
            self._warning("Bitte öffne zuerst ein Anki-Profil.")
            return
        try:
            config = self.mw.addonManager.getConfig(self.addon_package) or {}
            plan = plan_language_setup(
                collection, config, self.name_input.text(), self.code_input.text()
            )
        except LanguageSetupError as exc:
            self._warning(str(exc))
            return

        details = "\n".join(f"• {deck_name}" for deck_name in plan.deck_names)
        confirmed = QMessageBox.question(
            self,
            "Sprach-Deck einrichten",
            "Folgende lokale Änderungen werden vorgenommen:\n\n"
            f"• Notiztyp: {plan.note_type_name}\n"
            f"• Sprachcode für Speaking: {plan.language_code}\n"
            f"• Decks:\n{details}\n\n"
            "Es werden keine bestehenden Karten verschoben und keine Deck-Optionen oder "
            "Lernplanung verändert.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        try:
            self.mw.checkpoint(f"Sprach-Deck einrichten: {plan.display_name}")
            result = apply_language_setup(
                collection, self.mw.addonManager, self.addon_package, plan
            )
            self.mw.reset()
        except LanguageSetupError as exc:
            self._warning(str(exc))
            return
        QMessageBox.information(
            self,
            "Sprach-Deck eingerichtet",
            f"{result.note_type_name} und vier Skill-Decks wurden eingerichtet. "
            "Erstelle jetzt Notizen dieses Typs; das Sprach-Widget erscheint nur auf Speaking.",
        )
        self.accept()

    def _warning(self, message: str) -> None:
        QMessageBox.warning(self, "Sprach-Deck einrichten", message)


def install_language_setup_menu(mw: Any, addon_package: str) -> Any:
    """Add one Tools-menu action; no collection access happens until it is clicked."""
    from aqt.qt import QAction, QMenu

    menu = QMenu("Anki Speech Trainer", mw.form.menuTools)
    action = QAction("Sprach-Deck einrichten…", menu)
    action.triggered.connect(lambda: LanguageSetupDialog(mw, addon_package).exec())
    menu.addAction(action)
    mw.form.menuTools.addMenu(menu)
    return action
