from __future__ import annotations

from anki_speech_trainer.language_practice import (
    CARD_TEMPLATES,
    CSV_COLUMNS,
    FIELD_NAMES,
    NOTE_TYPE_NAME,
    REQUIRED_FIELDS,
    validate_rows,
)


def _row(**overrides: str) -> dict[str, str]:
    row = dict.fromkeys(FIELD_NAMES, "")
    row.update(
        {
            "ID": "it-a1-0001",
            "Prompt": "das Haus",
            "Target": "la casa",
            "TargetLanguageText": "La casa.",
            "Translation": "Das Haus.",
            "AudioTarget": "[sound:la-casa.mp3]",
            "EnableRecognition": "1",
            "EnableSpeaking": "1",
            "EnableWriting": "1",
            "EnableListening": "1",
        }
    )
    row.update(overrides)
    return row


def test_generic_source_has_neutral_fields_and_skill_templates() -> None:
    assert NOTE_TYPE_NAME == "Language Practice"
    assert "ItalianText" not in FIELD_NAMES
    assert "TranslationDE" not in FIELD_NAMES
    assert "TargetLanguageText" in FIELD_NAMES
    assert "Translation" in FIELD_NAMES
    assert CSV_COLUMNS == (*FIELD_NAMES, "Tags")
    assert [template.name for template in CARD_TEMPLATES] == [
        "Recognition",
        "Speaking",
        "Writing",
        "Listening",
    ]


def test_generic_templates_never_contain_an_italian_specific_prompt() -> None:
    rendered_source = "\n".join(
        f"{template.question_format}\n{template.answer_format}" for template in CARD_TEMPLATES
    ).casefold()

    assert "italien" not in rendered_source
    assert "{{targetlanguagetext}}" in rendered_source


def test_speaking_template_offers_a_native_typed_fallback() -> None:
    speaking = next(template for template in CARD_TEMPLATES if template.name == "Speaking")

    assert "{{type:Target}}" in speaking.question_format
    assert "lp-typed-fallback" in speaking.question_format
    assert "Ich kann gerade nicht sprechen" in speaking.question_format


def test_generic_required_fields_match_the_neutral_schema() -> None:
    assert REQUIRED_FIELDS["Recognition"] == (
        "EnableRecognition",
        "TargetLanguageText",
        "Translation",
    )
    assert REQUIRED_FIELDS["Listening"] == (
        "EnableListening",
        "AudioTarget",
        "TargetLanguageText",
        "Translation",
    )


def test_generic_validator_accepts_complete_source_data() -> None:
    assert validate_rows([_row()]) == ()
