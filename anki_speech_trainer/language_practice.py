"""Declarative source for the neutral, importable Language Practice note type.

It is the immutable source schema for the explicit language-deck setup assistant.
Each selected language receives a separate cloned note type and deck tree, so no
per-note language code is necessary.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

NOTE_TYPE_NAME = "Language Practice"
FIELD_NAMES = (
    "ID",
    "Prompt",
    "Target",
    "TargetLanguageText",
    "Translation",
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
    """One native Anki card template and its intended deck override."""

    name: str
    deck_name: str
    question_format: str
    answer_format: str


CARD_TEMPLATES = (
    CardTemplate(
        name="Recognition",
        deck_name="Language::Recognition",
        question_format="""{{#EnableRecognition}}
{{#TargetLanguageText}}
{{#Translation}}
<main class=\"lp-card lp-recognition\">
  <p class=\"lp-instruction\">Was bedeutet dieser Text in der Zielsprache?</p>
  <div class=\"lp-target-language\">{{TargetLanguageText}}</div>
  {{#Hint}}<aside class=\"lp-hint\">{{Hint}}</aside>{{/Hint}}
</main>
{{/Translation}}
{{/TargetLanguageText}}
{{/EnableRecognition}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"lp-card lp-answer\">
  <div class=\"lp-target-language\">{{TargetLanguageText}}</div>
  <div class=\"lp-translation\">{{Translation}}</div>
  {{#Hint}}<aside class=\"lp-hint\">{{Hint}}</aside>{{/Hint}}
</main>""",
    ),
    CardTemplate(
        name="Speaking",
        deck_name="Language::Speaking",
        question_format="""{{#EnableSpeaking}}
{{#Prompt}}
{{#Target}}
<main class=\"lp-card lp-speaking\">
  <p class=\"lp-instruction\">Sprich die passende Antwort in der Zielsprache.</p>
  <div class=\"lp-prompt\">{{Prompt}}</div>
  {{#Hint}}<aside class=\"lp-hint\">{{Hint}}</aside>{{/Hint}}
  <details class=\"lp-typed-fallback\">
    <summary>Ich kann gerade nicht sprechen</summary>
    <div class=\"lp-typed-answer\">
      <p>Tippe die Antwort stattdessen ein.</p>
      {{type:Target}}
    </div>
  </details>
</main>
{{/Target}}
{{/Prompt}}
{{/EnableSpeaking}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"lp-card lp-answer\">
  <div class=\"lp-target\">{{Target}}</div>
  {{#SpokenAlternatives}}
  <div class=\"lp-alternatives\">{{SpokenAlternatives}}</div>
  {{/SpokenAlternatives}}
  {{#TargetLanguageText}}
  <div class=\"lp-target-language\">{{TargetLanguageText}}</div>
  {{/TargetLanguageText}}
  {{#AudioTarget}}<div class=\"lp-audio\">{{AudioTarget}}</div>{{/AudioTarget}}
</main>""",
    ),
    CardTemplate(
        name="Writing",
        deck_name="Language::Writing",
        question_format="""{{#EnableWriting}}
{{#Prompt}}
{{#Target}}
<main class=\"lp-card lp-writing\">
  <p class=\"lp-instruction\">Schreib die passende Antwort in der Zielsprache.</p>
  <div class=\"lp-prompt\">{{Prompt}}</div>
  {{type:Target}}
  {{#Hint}}<aside class=\"lp-hint\">{{Hint}}</aside>{{/Hint}}
</main>
{{/Target}}
{{/Prompt}}
{{/EnableWriting}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"lp-card lp-answer\">
  <div class=\"lp-target\">{{Target}}</div>
  {{#TargetLanguageText}}
  <div class=\"lp-target-language\">{{TargetLanguageText}}</div>
  {{/TargetLanguageText}}
</main>""",
    ),
    CardTemplate(
        name="Listening",
        deck_name="Language::Listening",
        question_format="""{{#EnableListening}}
{{#AudioTarget}}
{{#TargetLanguageText}}
{{#Translation}}
<main class=\"lp-card lp-listening\">
  <p class=\"lp-instruction\">Was bedeutet das Gehörte?</p>
  <div class=\"lp-audio\">{{AudioTarget}}</div>
</main>
{{/Translation}}
{{/TargetLanguageText}}
{{/AudioTarget}}
{{/EnableListening}}""",
        answer_format="""{{FrontSide}}
<hr id=answer>
<main class=\"lp-card lp-answer\">
  <div class=\"lp-target-language\">{{TargetLanguageText}}</div>
  <div class=\"lp-translation\">{{Translation}}</div>
  <div class=\"lp-audio\">{{AudioTarget}}</div>
</main>""",
    ),
)

SHARED_CSS = """
.card { font-family: Arial, sans-serif; text-align: center; }
.lp-card { box-sizing: border-box; margin: 1em auto; max-width: 42rem; padding: 1rem; }
.lp-instruction { color: var(--fg, #333); font-size: 0.9em; margin: 0 0 1rem; }
.lp-prompt, .lp-target-language, .lp-target { font-size: 1.5em; line-height: 1.45; }
.lp-target { font-weight: 700; }
.lp-translation { margin-top: 0.75rem; font-size: 1.2em; }
.lp-hint, .lp-alternatives { margin-top: 1rem; color: var(--fg, #555); font-size: 0.95em; }
.lp-hint { border-left: 3px solid var(--border, #888); padding-left: 0.75rem; text-align: left; }
.lp-typed-fallback { margin-top: 1rem; }
.lp-typed-fallback summary {
  cursor: pointer;
  display: inline-block;
  min-height: 2.4em;
  box-sizing: border-box;
  padding: .55em .8em;
  border: 1px solid var(--border, #888);
  border-radius: .4em;
}
.lp-typed-fallback summary::-webkit-details-marker { display: none; }
.lp-typed-fallback summary:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
.lp-typed-answer { margin-top: .75rem; }
.nightMode .lp-card { color: #ddd; }
.nightMode .lp-hint { border-color: #aaa; }
""".strip()

REQUIRED_FIELDS = {
    "Recognition": ("EnableRecognition", "TargetLanguageText", "Translation"),
    "Speaking": ("EnableSpeaking", "Prompt", "Target"),
    "Writing": ("EnableWriting", "Prompt", "Target"),
    "Listening": ("EnableListening", "AudioTarget", "TargetLanguageText", "Translation"),
}


@dataclass(frozen=True)
class ValidationIssue:
    """A source-data issue safe to report without echoing learning content."""

    row_number: int
    code: str


def validate_rows(rows: Iterable[Mapping[str, object]]) -> tuple[ValidationIssue, ...]:
    """Validate import rows without opening an Anki collection or persisting data."""
    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        identifier = _text(row, "ID")
        if not identifier:
            issues.append(ValidationIssue(row_number, "missing_id"))
        elif identifier in seen_ids:
            issues.append(ValidationIssue(row_number, "duplicate_id"))
        else:
            seen_ids.add(identifier)

        enabled = [
            template_name
            for template_name, required in REQUIRED_FIELDS.items()
            if _text(row, required[0])
        ]
        if not enabled:
            issues.append(ValidationIssue(row_number, "no_enabled_card"))
        for template_name in enabled:
            missing = [
                field_name
                for field_name in REQUIRED_FIELDS[template_name][1:]
                if not _text(row, field_name)
            ]
            if missing:
                issues.append(ValidationIssue(row_number, f"missing_{template_name.lower()}_field"))
        if "Listening" in enabled and not _SOUND_TAG.search(_text(row, "AudioTarget")):
            issues.append(ValidationIssue(row_number, "listening_audio_not_sound_tag"))
    return tuple(issues)


def _text(row: Mapping[str, object], field_name: str) -> str:
    value = row.get(field_name, "")
    return value.strip() if isinstance(value, str) else ""
