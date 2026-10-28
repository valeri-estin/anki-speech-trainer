"""Declarative source for the optional, importable Italian Practice note type.

This module deliberately contains no Anki collection access. It is consumed by a
developer-side package builder and CSV validator, never by the review add-on at runtime.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

NOTE_TYPE_NAME = "Italian Practice"
FIELD_NAMES = (
    "ID",
    "Prompt",
    "Target",
    "ItalianText",
    "TranslationDE",
    "SpokenAlternatives",
    "Hint",
    "AudioTarget",
    "EnableRecognition",
    "EnableSpeaking",
    "EnableWriting",
    "EnableListening",
)
CSV_COLUMNS = (*FIELD_NAMES, "Tags")

_SOUND_TAG = re.compile(r"\[sound:[^\]]+\]", re.IGNORECASE)


@dataclass(frozen=True)
class CardTemplate:
    """One native Anki card template and its static deck override."""

    name: str
    deck_name: str
    question_format: str
    answer_format: str


CARD_TEMPLATES = (
    CardTemplate(
        name="Recognition",
        deck_name="Italian::Recognition",
        question_format="""{{#EnableRecognition}}
{{#ItalianText}}
{{#TranslationDE}}
<main class=\"ip-card ip-recognition\">
  <p class=\"ip-instruction\">Was bedeutet dieser italienische Text?</p>
  <div class=\"ip-italian\">{{ItalianText}}</div>
  {{#Hint}}<aside class=\"ip-hint\">{{Hint}}</aside>{{/Hint}}
</main>
{{/TranslationDE}}
{{/ItalianText}}
{{/EnableRecognition}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"ip-card ip-answer\">
  <div class=\"ip-italian\">{{ItalianText}}</div>
  <div class=\"ip-translation\">{{TranslationDE}}</div>
  {{#Hint}}<aside class=\"ip-hint\">{{Hint}}</aside>{{/Hint}}
</main>""",
    ),
    CardTemplate(
        name="Speaking",
        deck_name="Italian::Speaking",
        question_format="""{{#EnableSpeaking}}
{{#Prompt}}
{{#Target}}
<main class=\"ip-card ip-speaking\">
  <p class=\"ip-instruction\">Sprich die passende italienische Antwort.</p>
  <div class=\"ip-prompt\">{{Prompt}}</div>
  {{#Hint}}<aside class=\"ip-hint\">{{Hint}}</aside>{{/Hint}}
</main>
{{/Target}}
{{/Prompt}}
{{/EnableSpeaking}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"ip-card ip-answer\">
  <div class=\"ip-target\">{{Target}}</div>
  {{#SpokenAlternatives}}
  <div class=\"ip-alternatives\">{{SpokenAlternatives}}</div>
  {{/SpokenAlternatives}}
  {{#ItalianText}}<div class=\"ip-italian\">{{ItalianText}}</div>{{/ItalianText}}
  {{#AudioTarget}}<div class=\"ip-audio\">{{AudioTarget}}</div>{{/AudioTarget}}
</main>""",
    ),
    CardTemplate(
        name="Writing",
        deck_name="Italian::Writing",
        question_format="""{{#EnableWriting}}
{{#Prompt}}
{{#Target}}
<main class=\"ip-card ip-writing\">
  <p class=\"ip-instruction\">Schreib die passende italienische Antwort.</p>
  <div class=\"ip-prompt\">{{Prompt}}</div>
  {{type:Target}}
  {{#Hint}}<aside class=\"ip-hint\">{{Hint}}</aside>{{/Hint}}
</main>
{{/Target}}
{{/Prompt}}
{{/EnableWriting}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"ip-card ip-answer\">
  <div class=\"ip-target\">{{Target}}</div>
  {{#ItalianText}}<div class=\"ip-italian\">{{ItalianText}}</div>{{/ItalianText}}
</main>""",
    ),
    CardTemplate(
        name="Listening",
        deck_name="Italian::Listening",
        question_format="""{{#EnableListening}}
{{#AudioTarget}}
{{#ItalianText}}
{{#TranslationDE}}
<main class=\"ip-card ip-listening\">
  <p class=\"ip-instruction\">Was bedeutet das Gehörte?</p>
  <div class=\"ip-audio\">{{AudioTarget}}</div>
</main>
{{/TranslationDE}}
{{/ItalianText}}
{{/AudioTarget}}
{{/EnableListening}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"ip-card ip-answer\">
  <div class=\"ip-italian\">{{ItalianText}}</div>
  <div class=\"ip-translation\">{{TranslationDE}}</div>
  <div class=\"ip-audio\">{{AudioTarget}}</div>
</main>""",
    ),
)

SHARED_CSS = """
.card { font-family: Arial, sans-serif; text-align: center; }
.ip-card { box-sizing: border-box; margin: 1em auto; max-width: 42rem; padding: 1rem; }
.ip-instruction { color: var(--fg, #333); font-size: 0.9em; margin: 0 0 1rem; }
.ip-prompt, .ip-italian, .ip-target { font-size: 1.5em; line-height: 1.45; }
.ip-target { font-weight: 700; }
.ip-translation { margin-top: 0.75rem; font-size: 1.2em; }
.ip-hint, .ip-alternatives { margin-top: 1rem; color: var(--fg, #555); font-size: 0.95em; }
.ip-hint { border-left: 3px solid var(--border, #888); padding-left: 0.75rem; text-align: left; }
.nightMode .ip-card { color: #ddd; }
.nightMode .ip-hint { border-color: #aaa; }
""".strip()

REQUIRED_FIELDS = {
    "Recognition": ("EnableRecognition", "ItalianText", "TranslationDE"),
    "Speaking": ("EnableSpeaking", "Prompt", "Target"),
    "Writing": ("EnableWriting", "Prompt", "Target"),
    "Listening": ("EnableListening", "AudioTarget", "ItalianText", "TranslationDE"),
}


@dataclass(frozen=True)
class ValidationIssue:
    """A source-data issue safe to report without echoing learning content."""

    row_number: int
    code: str


def validate_rows(rows: Iterable[Mapping[str, str]]) -> tuple[ValidationIssue, ...]:
    """Validate import rows without opening an Anki collection or persisting data."""
    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        identifier = row.get("ID", "").strip()
        if not identifier:
            issues.append(ValidationIssue(row_number, "missing_id"))
        elif identifier in seen_ids:
            issues.append(ValidationIssue(row_number, "duplicate_id"))
        else:
            seen_ids.add(identifier)

        enabled = [
            template_name
            for template_name, required in REQUIRED_FIELDS.items()
            if row.get(required[0], "").strip()
        ]
        if not enabled:
            issues.append(ValidationIssue(row_number, "no_enabled_card"))
        for template_name in enabled:
            missing = [
                field_name
                for field_name in REQUIRED_FIELDS[template_name][1:]
                if not row.get(field_name, "").strip()
            ]
            if missing:
                issues.append(ValidationIssue(row_number, f"missing_{template_name.lower()}_field"))
        if "Listening" in enabled and not _SOUND_TAG.search(row.get("AudioTarget", "")):
            issues.append(ValidationIssue(row_number, "listening_audio_not_sound_tag"))
    return tuple(issues)
