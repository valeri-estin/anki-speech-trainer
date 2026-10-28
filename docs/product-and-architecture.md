# Product and architecture

## Product boundary

Anki Speech Trainer adds optional local speaking practice to mapped Anki
Desktop review cards. The learner clicks **Sprechen**, speaks an answer, reads a
local transcript and a conservative text-match indication, then chooses Anki's
normal rating. The add-on does not grade cards, alter FSRS or scheduling,
modify note content, provide pronunciation scores, or support AnkiDroid/iOS.

## Components

- The Anki add-on renders a namespaced reviewer widget only for an explicit
  note-type/template mapping.
- A separate local worker receives versioned JSON Lines through `QProcess`.
  It owns microphone capture, voice activity detection, Faster-Whisper, and
  matching.
- The worker is started on demand and keeps one model in memory. Its stdout is
  protocol-only; diagnostics go to stderr. The controller validates message
  schema, size, request identity, and review session identity before rendering
  a result.
- The worker receives an executable path and argument list, never a shell
  string. Stale responses, cancellation, worker exit, and timeouts take a
  recoverable UI path.

## Data and trust boundaries

Audio and transcript text remain in process memory and are released after an
attempt. The add-on writes no recording or transcript to the collection,
filesystem, telemetry, or cloud. Only the user's explicitly configured
note-type, template, answer field, and optional alternatives field are read.
Unmapped or invalid cards display no widget.

The local Python environment and Faster-Whisper model cache are external inputs.
Treat both as trusted local software: only use a virtual environment you
created, a known model identifier, and a model snapshot obtained from the
documented upstream source.
