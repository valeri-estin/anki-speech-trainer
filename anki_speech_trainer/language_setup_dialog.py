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
from .localization import language_from_config, text

_LANGUAGE_CODES = ("ru", "fr", "es", "en", "de", "pt", "pl", "nl", "uk", "tr", "ja", "ko", "zh")
_CUSTOM_INDEX = len(_LANGUAGE_CODES)


class LanguageSetupDialog(QDialog):
    """Preview collection changes, then create one isolated language setup."""

    def __init__(self, mw: Any, addon_package: str) -> None:
        super().__init__(mw)
        self.mw = mw
        self.addon_package = addon_package
        self.language = language_from_config(mw.addonManager.getConfig(addon_package) or {})
        self.setWindowTitle(self.copy("setup.title"))
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        explanation = QLabel(self.copy("setup.description"))
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        form = QFormLayout()
        self.language_choice = QComboBox(self)
        for code in _LANGUAGE_CODES:
            name = self.copy(f"language.{code}")
            self.language_choice.addItem(f"{name} ({code})", (name, code))
        self.language_choice.addItem(self.copy("setup.other_language"), None)
        self.name_input = QLineEdit(self)
        self.code_input = QLineEdit(self)
        self.code_input.setMaxLength(3)
        form.addRow(self.copy("setup.language"), self.language_choice)
        form.addRow(self.copy("setup.name"), self.name_input)
        form.addRow(self.copy("setup.code"), self.code_input)
        layout.addLayout(form)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok,
            parent=self,
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(self.copy("setup.preview"))
        self.buttons.accepted.connect(self._preview_and_apply)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.language_choice.currentIndexChanged.connect(self._update_inputs)
        self._update_inputs()

    def copy(self, key: str, **values: Any) -> str:
        return text(key, self.language, **values)

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
            self._warning(self.copy("setup.open_profile"))
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
            self.copy("setup.title"),
            self.copy(
                "setup.confirm",
                note_type=plan.note_type_name,
                code=plan.language_code,
                decks=details,
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        try:
            self.mw.checkpoint(self.copy("setup.checkpoint", name=plan.display_name))
            result = apply_language_setup(
                collection, self.mw.addonManager, self.addon_package, plan
            )
            self.mw.reset()
        except LanguageSetupError as exc:
            self._warning(str(exc))
            return
        QMessageBox.information(
            self,
            self.copy("setup.success_title"),
            self.copy("setup.success", note_type=result.note_type_name),
        )
        self.accept()

    def _warning(self, message: str) -> None:
        QMessageBox.warning(self, self.copy("setup.title"), message)


def install_language_setup_menu(mw: Any, addon_package: str) -> Any:
    """Add one Tools-menu action; no collection access happens until it is clicked."""
    from aqt.qt import QAction, QMenu

    menu = QMenu("Anki Speech Trainer", mw.form.menuTools)
    language = language_from_config(mw.addonManager.getConfig(addon_package) or {})
    action = QAction(text("setup.menu", language), menu)
    action.triggered.connect(lambda: LanguageSetupDialog(mw, addon_package).exec())
    menu.addAction(action)
    mw.form.menuTools.addMenu(menu)
    return action
