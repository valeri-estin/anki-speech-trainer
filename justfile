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
