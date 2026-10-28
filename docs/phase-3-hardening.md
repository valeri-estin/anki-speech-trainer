# Phase 3: hardening and verification status

## Completed developer checks

- `just check`: Ruff plus 31 deterministic tests for matching, protocol framing/limits, review
  state, stale controller messages, HTML-safe UI output, VAD timing, and worker error paths.
- Add-on package import against the installed Anki 26.09.3 Python 3.13/Qt 6 runtime.
- Direct long-lived worker startup with cached local Faster-Whisper `base` model, including a
  successful offline (`HF_HUB_OFFLINE=1`) model initialization.
- No worker audio/ML dependency enters the Anki runtime; no test or implementation mutates an
  Anki collection, note, card, deck, scheduler, media directory, or profile.

## Remaining acceptance evidence

The following cannot be completed in the current environment because `/dev/snd` and an interactive
desktop Anki test profile are unavailable:

1. Run `just spike --record --device DEVICE_ID` with a physical microphone and record the script's
   real timings and Italian transcript in a local test note (never save audio).
2. Link the add-on only into a separate Anki test profile and configure an exact mapping plus the
   absolute `.venv/bin/python` path.
3. Exercise A01–A09 from `02-SCOPE-ACCEPTANCE.md`, particularly card change during
   transcription, unplugged/wrong microphone, normal answer reveal/ease buttons, and an unmapped
   note type.
4. With the model already cached, disable network access and repeat one complete review run.

These are verification gaps, not known architecture deviations. No gamification feature was added.
