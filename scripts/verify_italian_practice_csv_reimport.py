#!/usr/bin/env python3
"""Verify that Italian Practice CSV source rows update by stable first-field ID."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Italian Practice .apkg")
    parser.add_argument("csv_path", type=Path, help="Italian Practice source CSV")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.package.is_file() or not args.csv_path.is_file():
        print("source_not_found", file=sys.stderr)
        return 2
    from anki.collection import Collection, ImportCsvRequest
    from anki.importing import ImportAnkiPackageOptions, ImportAnkiPackageRequest

    with tempfile.TemporaryDirectory(prefix="anki-speech-trainer-csv-") as directory:
        collection = Collection(str(Path(directory) / "csv-reimport.anki2"))
        try:
            collection.import_anki_package(
                ImportAnkiPackageRequest(
                    package_path=str(args.package),
                    options=ImportAnkiPackageOptions(
                        merge_notetypes=True,
                        with_scheduling=False,
                        with_deck_configs=True,
                    ),
                )
            )
            metadata = collection.get_csv_metadata(str(args.csv_path), None)
            collection.import_csv(ImportCsvRequest(path=str(args.csv_path), metadata=metadata))
            first_import_notes = collection.note_count()
            collection.import_csv(ImportCsvRequest(path=str(args.csv_path), metadata=metadata))
            if first_import_notes != 2 or collection.note_count() != first_import_notes:
                raise ValueError("csv_duplicate_or_missing_note")
            if len(collection.find_notes("ID:it-a1-0001")) != 1:
                raise ValueError("stable_id_not_updated")
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        finally:
            collection.close()
    print("Italian Practice CSV re-import is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
