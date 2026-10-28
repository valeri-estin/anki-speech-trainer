#!/usr/bin/env python3
"""Validate Italian Practice CSV source data before importing it into Anki."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anki_speech_trainer.italian_practice import CSV_COLUMNS, validate_rows  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="UTF-8 semicolon-separated source CSV")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with args.path.open("r", encoding="utf-8", newline="") as handle:
            rows = [line for line in handle if not line.startswith("#")]
        reader = csv.DictReader(rows, fieldnames=CSV_COLUMNS, delimiter=";")
        parsed_rows = list(reader)
        if any(None in row for row in parsed_rows):
            print("invalid_columns", file=sys.stderr)
            return 2
        issues = validate_rows(parsed_rows)
    except (OSError, UnicodeDecodeError, csv.Error):
        print("unreadable_csv", file=sys.stderr)
        return 2
    if issues:
        for issue in issues:
            print(f"row={issue.row_number} code={issue.code}", file=sys.stderr)
        return 1
    print("Italian Practice CSV is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
