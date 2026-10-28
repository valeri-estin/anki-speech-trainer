# Phase 3: hardening and verification status

## Completed developer checks

- `just check`: Ruff plus 31 deterministic tests for matching, protocol framing/limits, review
  state, stale controller messages, HTML-safe UI output, VAD timing, and worker error paths.
- Add-on package import against the installed Anki 26.09.3 Python 3.13/Qt 6 runtime.
- Anki 26.09.3 startup smoke test in a fresh temporary base/profile with an `addons21` symlink
  to this add-on, using Qt's offscreen platform. It stayed running until the controlled timeout
  without an add-on error on stderr; the temporary profile was removed afterward.
- Qt-IPC smoke test using Anki's bundled runtime: `ReviewController` started the external worker,
  received `model_ready`, sent `record_start`, surfaced the expected unavailable-microphone error,
  and then shut the worker down cleanly. This uses the real QProcess/JSONL path but no audio input.
- Direct long-lived worker startup with cached local Faster-Whisper `base` model, including a
  successful offline (`HF_HUB_OFFLINE=1`) model initialization.
- No worker audio/ML dependency enters the Anki runtime; no test or implementation mutates an
  Anki collection, note, card, deck, scheduler, media directory, or profile.

## Manual acceptance evidence and remaining coverage

On 2026-10-28, the developer reported successful completion of these physical-desktop checks:

1. `just spike --list-devices` and an explicit `just spike --record --device DEVICE_ID` run.
2. Local add-on symlink installation in a separate Anki test profile.
3. Exact `Basic` note-type to `Back` answer-field mapping with the absolute external worker
   interpreter.
4. Widget interaction on a mapped test card.
5. Cloze review card: no speech widget was rendered.
6. Answer reveal during an active interaction: no late speech result surfaced afterward.
7. Invalid or unavailable microphone: the expected recoverable error was shown.
8. Card change during an active interaction: the expected cancellation/stale-result behavior
   occurred.

The headless environment still cannot repeat those steps and the report did not include a stored
transcript or timing data. The following focused coverage remains useful before a tagged V1
release:

1. Optionally test an ordinary unmapped (non-Cloze) note type and each native ease button after a
   speech interaction. Cloze exclusion and result cancellation were manually verified above.
2. With the model already cached, disable network access and repeat one complete review run.

These are targeted verification gaps, not known architecture deviations. No gamification feature
was added.
