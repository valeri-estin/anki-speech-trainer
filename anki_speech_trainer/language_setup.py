"""Safe, explicit creation of one language-specific practice setup.

The review path remains read-only. This module is called only from a user-initiated
Tools-menu dialog after a preview and confirmation. It performs small, local Anki
collection changes without touching existing cards, notes, deck options, or scheduling.
"""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .italian_practice import FIELD_NAMES, NOTE_TYPE_NAME
from .localization import language_from_config, text

_LANGUAGE_CODE = re.compile(r"[a-z]{2,3}")
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")
_SKILL_NAMES = ("Recognition", "Speaking", "Writing", "Listening")


class LanguageSetupError(ValueError):
    """A safe, user-facing validation or setup failure."""


@dataclass(frozen=True)
class LanguageSetupPlan:
    """Validated, non-mutating description shown before collection changes."""

    display_name: str
    language_code: str
    note_type_name: str
    deck_names: tuple[str, ...]
    configuration: dict[str, Any]

    @property
    def mapping(self) -> dict[str, str]:
        return {
            "notetype_name": self.note_type_name,
            "card_template_name": "Speaking",
            "language": self.language_code,
            "answer_field": "Target",
            "alternatives_field": "SpokenAlternatives",
        }


@dataclass(frozen=True)
class LanguageSetupResult:
    """The exact objects created by a successful setup."""

    note_type_name: str
    deck_names: tuple[str, ...]
    language_code: str


def plan_language_setup(
    collection: Any,
    config: object,
    display_name: object,
    language_code: object,
) -> LanguageSetupPlan:
    """Validate a setup request without changing the collection or configuration."""
    name = _validated_display_name(display_name)
    code = _validated_language_code(language_code)
    if not isinstance(config, dict):
        raise LanguageSetupError(text("error.invalid_config"))
    ui_language = language_from_config(config)

    source = collection.models.by_name(NOTE_TYPE_NAME)
    if source is None:
        raise LanguageSetupError(text("error.source_missing", ui_language))
    _validate_source_notetype(source)

    note_type_name = f"{name} Practice"
    deck_names = tuple(f"{name}::{skill}" for skill in _SKILL_NAMES)
    if collection.models.by_name(note_type_name) is not None:
        raise LanguageSetupError(text("error.note_type_exists", ui_language, name=note_type_name))
    for deck_name in deck_names:
        if collection.decks.by_name(deck_name) is not None:
            raise LanguageSetupError(text("error.deck_exists", ui_language, name=deck_name))

    mappings = config.get("notetype_mappings", [])
    if not isinstance(mappings, list):
        raise LanguageSetupError(text("error.invalid_mappings", ui_language))
    if any(
        isinstance(mapping, dict) and mapping.get("notetype_name") == note_type_name
        for mapping in mappings
    ):
        raise LanguageSetupError(text("error.mapping_exists", ui_language, name=note_type_name))

    updated_config = deepcopy(config)
    updated_config["notetype_mappings"] = [
        *mappings,
        {
            "notetype_name": note_type_name,
            "card_template_name": "Speaking",
            "language": code,
            "answer_field": "Target",
            "alternatives_field": "SpokenAlternatives",
        },
    ]
    return LanguageSetupPlan(name, code, note_type_name, deck_names, updated_config)


def apply_language_setup(
    collection: Any,
    addon_manager: Any,
    addon_package: str,
    plan: LanguageSetupPlan,
) -> LanguageSetupResult:
    """Apply a previously reviewed plan and roll back only newly created objects on failure."""
    created_deck_ids: list[int] = []
    created_model_id: int | None = None
    try:
        deck_ids = {
            skill: collection.decks.id(deck_name)
            for skill, deck_name in zip(_SKILL_NAMES, plan.deck_names, strict=True)
        }
        created_deck_ids = list(deck_ids.values())
        source = collection.models.by_name(NOTE_TYPE_NAME)
        if source is None:
            raise LanguageSetupError(
                text("error.source_removed", language_from_config(plan.configuration))
            )
        _validate_source_notetype(source)
        cloned = collection.models.copy(source, add=False)
        cloned["name"] = plan.note_type_name
        for template in cloned["tmpls"]:
            template["did"] = deck_ids[template["name"]]
            _make_template_language_neutral(template)
        collection.models.add_dict(cloned)
        stored = collection.models.by_name(plan.note_type_name)
        if stored is None:
            raise LanguageSetupError(
                text("error.new_type_missing", language_from_config(plan.configuration))
            )
        created_model_id = int(stored["id"])
        addon_manager.writeConfig(addon_package, plan.configuration)
    except Exception as exc:
        _rollback(collection, created_model_id, created_deck_ids)
        if isinstance(exc, LanguageSetupError):
            raise
        raise LanguageSetupError(
            text("error.setup_failed", language_from_config(plan.configuration))
        ) from exc
    return LanguageSetupResult(plan.note_type_name, plan.deck_names, plan.language_code)


def _validated_display_name(value: object) -> str:
    if not isinstance(value, str):
        raise LanguageSetupError(text("error.invalid_language_name"))
    name = " ".join(value.split())
    if not name or len(name) > 80 or "::" in name or _CONTROL_CHARACTERS.search(value) is not None:
        raise LanguageSetupError(text("error.invalid_language_name"))
    return name


def _validated_language_code(value: object) -> str:
    code = value.strip().lower() if isinstance(value, str) else ""
    if _LANGUAGE_CODE.fullmatch(code) is None:
        raise LanguageSetupError(text("error.invalid_language_code"))
    return code


def _validate_source_notetype(notetype: Any) -> None:
    fields = notetype.get("flds") if isinstance(notetype, dict) else None
    templates = notetype.get("tmpls") if isinstance(notetype, dict) else None
    if not isinstance(fields, list) or not isinstance(templates, list):
        raise LanguageSetupError(text("error.source_incompatible"))
    field_names = tuple(field.get("name") for field in fields if isinstance(field, dict))
    template_names = tuple(
        template.get("name") for template in templates if isinstance(template, dict)
    )
    if field_names != FIELD_NAMES or template_names != _SKILL_NAMES:
        raise LanguageSetupError(text("error.source_modified"))


def _make_template_language_neutral(template: dict[str, Any]) -> None:
    for key in ("qfmt", "afmt"):
        value = template.get(key)
        if not isinstance(value, str):
            continue
        template[key] = value.replace("italienische Antwort", "Antwort in der Zielsprache").replace(
            "dieser italienische Text", "dieser Text in der Zielsprache"
        )


def _rollback(collection: Any, model_id: int | None, deck_ids: list[int]) -> None:
    """Best-effort cleanup limited to objects created by this invocation."""
    if model_id is not None:
        try:
            collection.models.remove(model_id)
        except Exception:
            pass
    if deck_ids:
        try:
            collection.decks.remove(deck_ids)
        except Exception:
            pass
