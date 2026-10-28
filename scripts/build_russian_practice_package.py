#!/usr/bin/env python3
"""Build the Russian Practice foundation package in a temporary collection."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anki_speech_trainer.language_practice import (  # noqa: E402
    CARD_TEMPLATES,
    FIELD_NAMES,
    SHARED_CSS,
)

NOTE_TYPE_NAME = "Russian Practice"
EXAMPLE_ID = "ru-a1-0001"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="destination .apkg file")
    return parser.parse_args()


def neutral_question_format(value: str) -> str:
    """Use English, target-language-neutral instructions in the cloned templates."""
    return (
        value.replace(
            "Was bedeutet dieser Text in der Zielsprache?",
            "What does this target-language text mean?",
        )
        .replace(
            "Sprich die passende Antwort in der Zielsprache.",
            "Speak the appropriate answer in the target language.",
        )
        .replace(
            "Schreib die passende Antwort in der Zielsprache.",
            "Write the appropriate answer in the target language.",
        )
        .replace("Was bedeutet das Gehörte?", "What does the recording mean?")
    )


def main() -> int:
    args = parse_args()
    from anki.collection import Collection, NoteIdsLimit
    from anki.exporting import ExportAnkiPackageOptions
    from anki.notes import Note

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="anki-speech-trainer-russian-package-") as directory:
        collection_path = Path(directory) / "Russian Practice.anki2"
        collection = Collection(str(collection_path))
        try:
            model = collection.models.new(NOTE_TYPE_NAME)
            for field_name in FIELD_NAMES:
                collection.models.add_field(model, collection.models.new_field(field_name))
            for specification in CARD_TEMPLATES:
                template = collection.models.new_template(specification.name)
                template["qfmt"] = neutral_question_format(specification.question_format)
                template["afmt"] = specification.answer_format
                # Package imports do not reliably remap deck-override IDs.
                template["did"] = None
                collection.models.add_template(model, template)
            model["css"] = SHARED_CSS
            collection.models.add(model)
            model = collection.models.by_name(NOTE_TYPE_NAME)
            if model is None:
                raise RuntimeError("Russian Practice note type was not created")

            example = Note(collection, model)
            example["ID"] = EXAMPLE_ID
            example["Prompt"] = "the house"
            example["Target"] = "дом"
            example["TargetLanguageText"] = "Дом."
            example["Translation"] = "The house."
            example["SpokenAlternatives"] = "дом"
            example["EnableRecognition"] = "1"
            example["EnableSpeaking"] = "1"
            example["EnableWriting"] = "1"
            example.tags = ["niveau::A1", "russian-practice::seed"]
            collection.add_note(example, deck_id=collection.decks.id("Russian Practice"))

            options = ExportAnkiPackageOptions(
                with_scheduling=False,
                with_deck_configs=True,
                with_media=True,
                legacy=True,
            )
            collection.export_anki_package(
                out_path=str(args.output), options=options, limit=NoteIdsLimit([example.id])
            )
        finally:
            collection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
