set quiet := true

# Default command: show available project workflows.
[private]
default: help

# List public project workflows.
help:
    @just --list

# Run the isolated microphone, VAD, and local transcription spike.
spike *args:
    .venv/bin/python scripts/audio_spike.py {{args}}

# Run the automated test suite without Anki or microphone hardware.
test:
    .venv/bin/python -m pytest -q

# Run static checks.
lint:
    .venv/bin/python -m ruff check .

# Run all automated quality checks.
check: lint test

# Apply safe automated formatting where supported.
format:
    .venv/bin/python -m ruff format .

# Validate Italian Practice CSV rows before an Anki import.
validate-italian-practice:
    .venv/bin/python scripts/validate_italian_practice_csv.py 'templates/italian-practice/Italian Practice.csv'

# Build the optional Italian Practice package using the installed Anki runtime.
build-italian-practice:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/build_italian_practice_package.py --output 'templates/italian-practice/Italian Practice.apkg'

# Verify the generated package without opening a user Anki profile.
verify-italian-practice:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/verify_italian_practice_package.py 'templates/italian-practice/Italian Practice.apkg'
