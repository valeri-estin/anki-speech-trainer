from __future__ import annotations

from anki_speech_trainer.italian_practice import (
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
            "ItalianText": "La casa.",
            "TranslationDE": "Das Haus.",
            "AudioTarget": "[sound:la-casa.mp3]",
            "EnableRecognition": "1",
            "EnableSpeaking": "1",
            "EnableWriting": "1",
            "EnableListening": "1",
        }
    )
    row.update(overrides)
    return row


def test_note_type_has_four_skill_templates_with_separate_decks() -> None:
    assert NOTE_TYPE_NAME == "Italian Practice"
    assert [template.name for template in CARD_TEMPLATES] == [
        "Recognition",
        "Speaking",
        "Writing",
        "Listening",
    ]
    assert [template.deck_name for template in CARD_TEMPLATES] == [
        "Italian::Recognition",
        "Italian::Speaking",
        "Italian::Writing",
        "Italian::Listening",
    ]
    assert CSV_COLUMNS == (*FIELD_NAMES, "Tags")


def test_speaking_template_hides_the_target_on_the_question_side() -> None:
    speaking = next(template for template in CARD_TEMPLATES if template.name == "Speaking")

    assert "{{Target}}" not in speaking.question_format
    assert "{{Target}}" in speaking.answer_format


def test_speaking_template_offers_a_native_typed_fallback() -> None:
    speaking = next(template for template in CARD_TEMPLATES if template.name == "Speaking")

    assert "{{type:Target}}" in speaking.question_format
    assert "ip-typed-fallback" in speaking.question_format
    assert "Ich kann gerade nicht sprechen" in speaking.question_format


def test_each_template_requires_its_enable_field_and_required_content() -> None:
    for template in CARD_TEMPLATES:
        for field_name in REQUIRED_FIELDS[template.name]:
            assert f"{{{{#{field_name}}}}}" in template.question_format


def test_validator_accepts_a_complete_row() -> None:
    assert validate_rows([_row()]) == ()


def test_validator_rejects_duplicate_ids_and_missing_listening_audio() -> None:
    invalid_listening = _row(AudioTarget="not-an-anki-sound")

    issues = validate_rows([_row(), invalid_listening])

    assert {(issue.row_number, issue.code) for issue in issues} == {
        (3, "duplicate_id"),
        (3, "listening_audio_not_sound_tag"),
    }


def test_validator_rejects_enabled_cards_without_their_required_fields() -> None:
    issues = validate_rows([_row(Target="")])

    assert {(issue.row_number, issue.code) for issue in issues} == {
        (2, "missing_speaking_field"),
        (2, "missing_writing_field"),
    }


def test_validator_treats_missing_values_as_invalid_instead_of_crashing() -> None:
    row = _row(
        ID=None,
        EnableRecognition="",
        EnableSpeaking="",
        EnableWriting="",
        EnableListening="",
    )

    assert {(issue.row_number, issue.code) for issue in validate_rows([row])} == {
        (2, "missing_id"),
        (2, "no_enabled_card"),
    }
