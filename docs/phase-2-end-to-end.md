# Phase 2: worker end-to-end path

## Implemented flow

1. A click on **Sprechen** creates (or reuses) a `QProcess` worker and sends `configure`.
2. The worker loads the multilingual Faster-Whisper model once, returns `model_ready`, and keeps
   it warm for subsequent configured cards.
3. The controller sends `record_start` only after that acknowledgement. The worker opens the
   microphone, captures in-memory PCM16 with WebRTC VAD, retains 300 ms pre-roll, and stops after
   the configured speech pause. It accepts cancellation while capture is active.
4. The worker transcribes without an expected-answer prompt, with `language=it`, CPU `int8`,
   `beam_size=1`, and `condition_on_previous_text=False`. PCM is immediately released after
   inference.
5. The controller ignores stale session results, compares the transcript conservatively with the
   mapped answer and explicit alternatives, and displays only a text indication. It has no Anki
   answer, scheduling, database, or card-navigation call.

The controller accepts a `model_ready` reply only for the active configure request and accepts a
transcript, cancellation, or recording status only for the active recording request. This extends
the session-ID protection to repeated attempts on the same card.

Cancellation invalidates both active request IDs and restores the widget immediately to `Bereit`;
the later worker cancellation acknowledgement is intentionally ignored as stale.

The controller bounds an initial model-ready wait to two minutes and a complete recording-to-result
wait to 90 seconds. A timeout affects only the captured worker instance, renders a recoverable
error, and terminates that process without waiting on Anki's GUI thread. Late timer callbacks and
signals from an old process are discarded; its expected exit does not overwrite the timeout
message with a second generic error.

## Local worker verification

The real isolated worker accepted `configure` for the cached Faster-Whisper `base` model and
returned these protocol events on 2026-10-28:

```text
status initializing
status model_ready (307 ms model load)
cancelled (shutdown)
```

This validates the local model process, JSONL framing, and warm-model initialization. It does not
validate audio capture or real Italian transcription: the current session has no accessible
microphone. A real test profile and microphone remain the concrete blocker for the V1 end-to-end
acceptance scenario.

The same command with `HF_HUB_OFFLINE=1` returned `model_ready` in **329 ms**, demonstrating that
the cached model loads without a network request. This confirms the offline behavior only for the
already cached `base` snapshot; initial model provisioning still needs network access.

## Lifecycle behavior

Question changes, answer reveal, and profile closing cancel in-flight work. Profile close first
sends `shutdown`; after two seconds, a still-running process is terminated without blocking Anki's
GUI thread. Opening a profile resets controller state. The worker validates requests before use,
rejects a second recording as `busy`, and emits recoverable error codes for microphone, silence,
duration, model, and transcription failures.
