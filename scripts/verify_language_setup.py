#!/usr/bin/env python3
"""Verify the explicit language setup flow with a temporary real Anki collection."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anki_speech_trainer.italian_practice import FIELD_NAMES, NOTE_TYPE_NAME  # noqa: E402
from anki_speech_trainer.language_setup import (  # noqa: E402
    LanguageSetupError,
    apply_language_setup,
    plan_language_setup,
)


class TemporaryAddonManager:
    """Keep the test configuration in memory instead of an Anki user profile."""

    def __init__(self) -> None:
        self.config = {
            "enabled": True,
            "notetype_mappings": [
                {
                    "notetype_name": "Basic",
                    "answer_field": "Back",
                    "alternatives_field": "",
                }
            ],
        }

    def getConfig(self, _addon_package: str) -> dict:
        return self.config

    def writeConfig(self, _addon_package: str, config: dict) -> None:
        self.config = config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Italian Practice .apkg")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.path.is_file():
        print("package_not_found", file=sys.stderr)
        return 2
    from anki.collection import Collection
    from anki.importing import ImportAnkiPackageOptions, ImportAnkiPackageRequest

    with tempfile.TemporaryDirectory(prefix="anki-speech-trainer-language-setup-") as directory:
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
            manager = TemporaryAddonManager()
            plan = plan_language_setup(collection, manager.config, "Russisch", "ru")
            result = apply_language_setup(collection, manager, "anki_speech_trainer", plan)
            if result.note_type_name != "Russisch Practice":
                raise ValueError("unexpected_result")
            source = collection.models.by_name(NOTE_TYPE_NAME)
            cloned = collection.models.by_name(result.note_type_name)
            if source is None or cloned is None:
                raise ValueError("missing_notetype")
            if [field["name"] for field in cloned["flds"]] != list(FIELD_NAMES):
                raise ValueError("unexpected_cloned_fields")
            for template in source["tmpls"]:
                if template["did"] is not None:
                    raise ValueError("source_notetype_changed")
            for template in cloned["tmpls"]:
                expected_deck = f"Russisch::{template['name']}"
                if template["did"] != collection.decks.id(expected_deck, create=False):
                    raise ValueError("unexpected_deck_override")
                if "italienische" in template["qfmt"].casefold():
                    raise ValueError("language_specific_copy")
            if manager.config["notetype_mappings"][-1] != plan.mapping:
                raise ValueError("unexpected_mapping")
            if collection.note_count() != 1:
                raise ValueError("unexpected_notes_created")
            try:
                plan_language_setup(collection, manager.config, "Russisch", "ru")
            except LanguageSetupError:
                pass
            else:
                raise ValueError("duplicate_setup_not_rejected")
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        finally:
            collection.close()
    print("Language setup is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
