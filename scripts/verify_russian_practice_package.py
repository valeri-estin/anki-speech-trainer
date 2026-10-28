#!/usr/bin/env python3
"""Verify the generated Russian Practice package in a temporary collection."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anki_speech_trainer.italian_practice import CARD_TEMPLATES, FIELD_NAMES  # noqa: E402
from scripts.build_russian_practice_package import EXAMPLE_ID, NOTE_TYPE_NAME  # noqa: E402

EXPECTED_INSTRUCTIONS = {
    "Recognition": "What does this target-language text mean?",
    "Speaking": "Speak the appropriate answer in the target language.",
    "Writing": "Write the appropriate answer in the target language.",
    "Listening": "What does the recording mean?",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Russian Practice .apkg to verify")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.path.is_file():
        print("package_not_found", file=sys.stderr)
        return 2
    try:
        from anki.collection import Collection
        from anki.importing import ImportAnkiPackageOptions, ImportAnkiPackageRequest

        with tempfile.TemporaryDirectory(prefix="anki-speech-trainer-russian-verify-") as directory:
            collection = Collection(str(Path(directory) / "verification.anki2"))
            try:
                collection.import_anki_package(
                    ImportAnkiPackageRequest(
                        package_path=str(args.path),
                        options=ImportAnkiPackageOptions(
                            merge_notetypes=True,
                            with_scheduling=False,
                            with_deck_configs=True,
                        ),
                    )
                )
                model = collection.models.by_name(NOTE_TYPE_NAME)
                if model is None:
                    raise ValueError("missing_note_type")
                if [field["name"] for field in model["flds"]] != list(FIELD_NAMES):
                    raise ValueError("unexpected_fields")
                templates = {template["name"]: template for template in model["tmpls"]}
                for specification in CARD_TEMPLATES:
                    template = templates.get(specification.name)
                    if template is None or template["did"] is not None:
                        raise ValueError("unexpected_template")
                    if EXPECTED_INSTRUCTIONS[specification.name] not in template["qfmt"]:
                        raise ValueError("unexpected_template_instruction")
                if collection.note_count() != 1 or collection.card_count() != 3:
                    raise ValueError("unexpected_example_cards")
                note_id = collection.find_notes(f'\"ID:{EXAMPLE_ID}\"')
                if len(note_id) != 1:
                    raise ValueError("missing_example_note")
                if len(collection.find_notes("tag:russian-practice::seed")) != 1:
                    raise ValueError("missing_seed_tag")
            finally:
                collection.close()
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Russian Practice package is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
