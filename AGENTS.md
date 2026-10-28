# Project instructions

Anki Speech Trainer V1 is an Anki Desktop add-on for local active speaking
practice, not a standalone flashcard system.

## Before changing the project

1. Read the README and all current files in `docs/`, including verification
   records and examples.
2. Check the installed Anki version and bundled Python runtime before using an
   Anki hook. Document version-dependent API choices.
3. Preserve existing Anki decks, note types, templates, media, and scheduler
   state. Do not write directly to an Anki collection database.

## Architecture constraints

- Use only Anki's built-in Python/Qt environment in the add-on. Heavy
  dependencies (`faster-whisper`, `ctranslate2`, `sounddevice`,
  `webrtcvad-wheels`, and NumPy) run only in a separate local worker
  interpreter.
- Start one long-lived worker on demand. Do not initialize the model per card.
- Activate the microphone only after an explicit click; stop on speech pause and
  cancel recording on card changes or Anki shutdown.
- Use versioned JSON Lines over stdin/stdout. stdout is machine-readable
  protocol data only; diagnostics go to stderr. Never launch a shell.
- Keep the UI thread responsive and ensure worker failures cannot break review.
- Read only explicitly configured note types/fields. Never automate Anki
  ratings or `showAnswer`.
- Store no audio or transcript, send no telemetry, and use no cloud STT.

## Quality and release

- Keep changes small and testable. Update `CHANGELOG.md` for user-visible
  changes.
- Run Ruff and pytest for runtime, test, or packaging changes. Use an isolated
  Anki test profile for integration checks.
- Keep code, comments, and documentation in English. German is intentional only
  for the current user-facing add-on interface.
- Never package model weights, virtual environments, caches, bytecode, or
  Anki-generated `meta.json`.
- Do not push without an explicitly configured remote and successful checks.
