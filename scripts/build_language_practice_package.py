#!/usr/bin/env python3
"""Build the neutral Language Practice .apkg in an isolated temporary collection."""
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
    NOTE_TYPE_NAME,
    SHARED_CSS,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="destination .apkg file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from anki.collection import Collection, NoteIdsLimit
    from anki.exporting import ExportAnkiPackageOptions
    from anki.notes import Note

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="anki-speech-trainer-language-package-") as directory:
        collection = Collection(str(Path(directory) / "Language Practice.anki2"))
        try:
            model = collection.models.new(NOTE_TYPE_NAME)
            for field_name in FIELD_NAMES:
                collection.models.add_field(model, collection.models.new_field(field_name))
            for specification in CARD_TEMPLATES:
                template = collection.models.new_template(specification.name)
                template["qfmt"] = specification.question_format
                template["afmt"] = specification.answer_format
                template["did"] = None
                collection.models.add_template(model, template)
            model["css"] = SHARED_CSS
            collection.models.add(model)
            model = collection.models.by_name(NOTE_TYPE_NAME)
            if model is None:
                raise RuntimeError("Language Practice note type was not created")

            example = Note(collection, model)
            example["ID"] = "it-a1-0001"
            example["Prompt"] = "das Haus"
            example["Target"] = "la casa"
            example["TargetLanguageText"] = "La casa."
            example["Translation"] = "Das Haus."
            example["SpokenAlternatives"] = "casa"
            example["EnableRecognition"] = "1"
            example["EnableSpeaking"] = "1"
            example["EnableWriting"] = "1"
            example.tags = ["language-practice::seed", "niveau::A1"]
            collection.add_note(example, deck_id=collection.decks.id(NOTE_TYPE_NAME))

            collection.export_anki_package(
                out_path=str(args.output),
                options=ExportAnkiPackageOptions(
                    with_scheduling=False,
                    with_deck_configs=True,
                    with_media=True,
                    legacy=True,
                ),
                limit=NoteIdsLimit([example.id]),
            )
        finally:
            collection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
