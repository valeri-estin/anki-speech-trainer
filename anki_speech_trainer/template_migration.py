"""Explicit, previewable migration for native typed Speaking fallbacks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .localization import language_from_config, text

_FALLBACK_MARKER = "data-ast-typed-fallback"
_SAFE_FIELD_NAME = re.compile(r"[^{}<>]+")


class SpeakingTemplateUpdateError(ValueError):
    """A safe error raised when a reviewed template cannot be updated."""


@dataclass(frozen=True)
class SkippedTemplate:
    note_type_name: str
    template_name: str
    reason: str


@dataclass(frozen=True)
class SpeakingTemplateUpdate:
    note_type_name: str
    template_name: str
    original_question_format: str
    updated_question_format: str


@dataclass(frozen=True)
class SpeakingTemplateUpdatePlan:
    updates: tuple[SpeakingTemplateUpdate, ...]
    skipped: tuple[SkippedTemplate, ...]


@dataclass(frozen=True)
class SpeakingTemplateUpdateResult:
    updated: tuple[tuple[str, str], ...]


def plan_speaking_template_update(
    collection: Any, config: object
) -> SpeakingTemplateUpdatePlan:
    """Describe scoped Speaking-template updates without writing a collection."""
    if not isinstance(config, dict) or not isinstance(config.get("notetype_mappings"), list):
        raise SpeakingTemplateUpdateError(text("error.invalid_mappings"))

    language = language_from_config(config)
    updates: list[SpeakingTemplateUpdate] = []
    skipped: list[SkippedTemplate] = []
    seen: set[tuple[str, str]] = set()
    for mapping in config["notetype_mappings"]:
        if not isinstance(mapping, dict):
            continue
        note_type_name = mapping.get("notetype_name")
        template_name = mapping.get("card_template_name")
        answer_field = mapping.get("answer_field")
        if not isinstance(note_type_name, str) or not note_type_name:
            continue
        if template_name != "Speaking":
            skipped.append(SkippedTemplate(note_type_name, "Speaking", "template_not_scoped"))
            continue
        if not isinstance(answer_field, str) or not answer_field:
            skipped.append(SkippedTemplate(note_type_name, template_name, "answer_field_missing"))
            continue
        identifier = (note_type_name, template_name)
        if identifier in seen:
            continue
        seen.add(identifier)
        model = collection.models.by_name(note_type_name)
        if not isinstance(model, dict):
            skipped.append(SkippedTemplate(note_type_name, template_name, "note_type_missing"))
            continue
        field_names = {
            field.get("name")
            for field in model.get("flds", [])
            if isinstance(field, dict) and isinstance(field.get("name"), str)
        }
        if answer_field not in field_names or _SAFE_FIELD_NAME.fullmatch(answer_field) is None:
            skipped.append(SkippedTemplate(note_type_name, template_name, "answer_field_invalid"))
            continue
        template = _template(model, template_name)
        if template is None:
            skipped.append(SkippedTemplate(note_type_name, template_name, "template_missing"))
            continue
        question_format = template.get("qfmt")
        if not isinstance(question_format, str):
            skipped.append(SkippedTemplate(note_type_name, template_name, "template_invalid"))
            continue
        if _has_typed_fallback(question_format, answer_field):
            skipped.append(SkippedTemplate(note_type_name, template_name, "already_updated"))
            continue
        updates.append(
            SpeakingTemplateUpdate(
                note_type_name,
                template_name,
                question_format,
                f"{question_format}\n{typed_fallback_markup(answer_field, language)}",
            )
        )
    return SpeakingTemplateUpdatePlan(tuple(updates), tuple(skipped))


def apply_speaking_template_update(
    collection: Any, plan: SpeakingTemplateUpdatePlan
) -> SpeakingTemplateUpdateResult:
    """Apply a reviewed update plan, rejecting stale or changed templates first."""
    _verify_plan_is_current(collection, plan)
    originals: list[dict[str, Any]] = []
    try:
        for update in plan.updates:
            model = collection.models.by_name(update.note_type_name)
            if not isinstance(model, dict):
                raise SpeakingTemplateUpdateError(text("error.template_update_stale"))
            template = _template(model, update.template_name)
            if template is None:
                raise SpeakingTemplateUpdateError(text("error.template_update_stale"))
            originals.append({"model": model, "qfmt": template["qfmt"]})
            template["qfmt"] = update.updated_question_format
            collection.models.update_dict(model)
    except Exception as exc:
        for original in reversed(originals):
            try:
                template = _template(original["model"], "Speaking")
                if template is not None:
                    template["qfmt"] = original["qfmt"]
                    collection.models.update_dict(original["model"])
            except Exception:
                pass
        if isinstance(exc, SpeakingTemplateUpdateError):
            raise
        raise SpeakingTemplateUpdateError(text("error.template_update_failed")) from exc
    return SpeakingTemplateUpdateResult(
        tuple((update.note_type_name, update.template_name) for update in plan.updates)
    )


def typed_fallback_markup(answer_field: str, language: str) -> str:
    """Return trusted static template markup for one validated Anki field name."""
    return """<details class=\"ast-typed-fallback\" data-ast-typed-fallback>
  <summary>{label}</summary>
  <div class=\"ast-typed-answer\">
    <p>{description}</p>
    {{{{type:{answer_field}}}}}
  </div>
</details>
<style>
.ast-typed-fallback {{ margin-top: 1rem; }}
.ast-typed-fallback summary {{
  cursor: pointer;
  display: inline-block;
  min-height: 2.4em;
  box-sizing: border-box;
  padding: .55em .8em;
  border: 1px solid var(--border, #888);
  border-radius: .4em;
}}
.ast-typed-fallback summary::-webkit-details-marker {{ display: none; }}
.ast-typed-fallback summary:focus-visible {{
  outline: 2px solid currentColor;
  outline-offset: 2px;
}}
.ast-typed-answer {{ margin-top: .75rem; }}
</style>""".format(
        label=text("template.fallback.label", language),
        description=text("template.fallback.description", language),
        answer_field=answer_field,
    )


def _template(model: dict[str, Any], template_name: str) -> dict[str, Any] | None:
    for template in model.get("tmpls", []):
        if isinstance(template, dict) and template.get("name") == template_name:
            return template
    return None


def _has_typed_fallback(question_format: str, answer_field: str) -> bool:
    return _FALLBACK_MARKER in question_format or (
        "typed-fallback" in question_format and f"{{{{type:{answer_field}}}}}" in question_format
    )


def _verify_plan_is_current(collection: Any, plan: SpeakingTemplateUpdatePlan) -> None:
    for update in plan.updates:
        model = collection.models.by_name(update.note_type_name)
        template = _template(model, update.template_name) if isinstance(model, dict) else None
        if template is None or template.get("qfmt") != update.original_question_format:
            raise SpeakingTemplateUpdateError(text("error.template_update_stale"))
