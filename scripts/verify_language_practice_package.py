#!/usr/bin/env python3
"""Verify the neutral Language Practice package in a temporary collection."""

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
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Language Practice .apkg to verify")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.path.is_file():
        print("package_not_found", file=sys.stderr)
        return 2
    try:
        from anki.collection import Collection
        from anki.importing import ImportAnkiPackageOptions, ImportAnkiPackageRequest

        with tempfile.TemporaryDirectory(
            prefix="anki-speech-trainer-language-verify-"
        ) as directory:
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
                    if "italien" in template["qfmt"].casefold():
                        raise ValueError("language_specific_template")
                speaking = templates["Speaking"]["qfmt"]
                if "{{type:Target}}" not in speaking or "lp-typed-fallback" not in speaking:
                    raise ValueError("missing_typed_fallback")
                if collection.note_count() != 1 or collection.card_count() != 3:
                    raise ValueError("unexpected_example_cards")
            finally:
                collection.close()
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Language Practice package is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
