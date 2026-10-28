#!/usr/bin/env python3
"""Smoke-test imported Italian Practice cards against Anki's real review mapping API."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anki_speech_trainer.controller import CardMapping, ReviewController


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Italian Practice .apkg to smoke-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.path.is_file():
        print("package_not_found", file=sys.stderr)
        return 2
    from anki.collection import Collection
    from anki.importing import ImportAnkiPackageOptions, ImportAnkiPackageRequest
    from aqt.qt import QCoreApplication

    QCoreApplication.instance() or QCoreApplication([])
    config = {
        "enabled": True,
        "language": "ru",
        "notetype_mappings": [
            {
                "notetype_name": "Italian Practice",
                "card_template_name": "Speaking",
                "language": "it",
                "answer_field": "Target",
                "alternatives_field": "SpokenAlternatives",
            }
        ],
    }
    with tempfile.TemporaryDirectory(prefix="anki-speech-trainer-integration-") as directory:
        collection = Collection(str(Path(directory) / "integration.anki2"))
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
            note_ids = collection.find_notes("ID:it-a1-0001")
            if len(note_ids) != 1:
                raise ValueError("example_note_not_found")
            note = collection.get_note(note_ids[0])
            cards = [collection.get_card(card_id) for card_id in note.card_ids()]
            cards_by_template = {card.template()["name"]: card for card in cards}
            controller = ReviewController(
                SimpleNamespace(addonManager=SimpleNamespace(getConfig=lambda _name: config))
            )
            import anki.utils

            original_strip_html = anki.utils.strip_html
            # A temporary Collection has no running Anki text-processing backend. The controller's
            # real-card/template mapping is still exercised; HTML stripping has dedicated tests.
            anki.utils.strip_html = lambda value: value
            try:
                mapping = controller.mapping_for_card(cards_by_template["Speaking"])
                if mapping != CardMapping("la casa", ("casa",), "it"):
                    raise ValueError("speaking_mapping_failed")
                if controller.mapping_for_card(cards_by_template["Writing"]) is not None:
                    raise ValueError("writing_widget_not_excluded")
                if controller.mapping_for_card(cards_by_template["Recognition"]) is not None:
                    raise ValueError("recognition_widget_not_excluded")
            finally:
                anki.utils.strip_html = original_strip_html
        except (KeyError, OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        finally:
            collection.close()
    print("Italian Practice Anki integration is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
