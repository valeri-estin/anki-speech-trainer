"""Build a minimal, installable Anki Speech Trainer archive."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ADDON_ROOT = ROOT / "anki_speech_trainer"


def runtime_files() -> list[Path]:
    return sorted(
        file
        for file in ADDON_ROOT.rglob("*")
        if file.is_file()
        and "__pycache__" not in file.parts
        and file.name != "meta.json"
        and file.suffix not in {".pyc", ".pyo"}
    )


def main() -> None:
    manifest = json.loads((ADDON_ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = manifest["human_version"]
    output = ROOT / "dist" / f"anki-speech-trainer-{version}.ankiaddon"
    output.parent.mkdir(exist_ok=True)

    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for file in runtime_files():
            archive.write(file, file.relative_to(ADDON_ROOT).as_posix())

    with ZipFile(output) as archive:
        names = set(archive.namelist())
    required = {"__init__.py", "config.json", "manifest.json", "worker/main.py"}
    if not required.issubset(names):
        raise RuntimeError(f"Invalid add-on archive; missing {sorted(required - names)}")
    print(output)


if __name__ == "__main__":
    main()
