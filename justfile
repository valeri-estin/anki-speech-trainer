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

# Check pinned Python dependencies against known vulnerability advisories.
audit-deps:
    .venv/bin/python -m pip check
    .venv/bin/python -m pip_audit -r requirements-worker.txt

# Build a minimal installable .ankiaddon archive.
build-addon:
    .venv/bin/python scripts/build_addon.py

# Run all automated quality checks and verify the package can be built.
check: lint test build-addon

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

# Smoke-test imported Italian Practice cards against the installed Anki review API.
verify-italian-practice-integration:
    QT_QPA_PLATFORM=offscreen PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/verify_italian_practice_integration.py 'templates/italian-practice/Italian Practice.apkg'

# Verify that a repeated CSV import updates stable Italian Practice IDs without duplicates.
verify-italian-practice-csv-reimport:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/verify_italian_practice_csv_reimport.py 'templates/italian-practice/Italian Practice.apkg' 'templates/italian-practice/Italian Practice.csv'

# Build the Russian Practice foundation package for direct deck generation.
build-russian-practice:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/build_russian_practice_package.py --output 'templates/russian-practice/Russian Practice.apkg'

# Verify the Russian Practice foundation package in an isolated temporary collection.
verify-russian-practice:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/verify_russian_practice_package.py 'templates/russian-practice/Russian Practice.apkg'

# Verify language setup against the installed Anki collection API in a temporary collection.
verify-language-setup:
    PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/verify_language_setup.py 'templates/italian-practice/Italian Practice.apkg'

# Smoke-test the user-visible language setup menu with Anki's Qt runtime.
verify-language-setup-menu:
    QT_QPA_PLATFORM=offscreen PYTHONPATH="/usr/local/share/anki/app_packages:{{justfile_directory()}}" /usr/local/share/anki/python/bin/python3.13 scripts/verify_language_setup_menu.py
