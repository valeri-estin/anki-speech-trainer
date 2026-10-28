# Anki Speech Trainer configuration

Configuration is stored in Anki's add-on configuration. A missing or invalid mapping is safe:
no speech widget is displayed and no card, note, or scheduler state is modified.

```json
{
  "enabled": true,
  "worker_python": "/absolute/path/to/anki-speech-trainer/.venv/bin/python",
  "language": "it",
  "model": "base",
  "device": "cpu",
  "compute_type": "int8",
  "microphone_device_id": null,
  "auto_stop_silence_ms": 800,
  "max_record_seconds": 12,
  "notetype_mappings": [
    {
      "notetype_name": "Italiano A1",
      "answer_field": "Italiano",
      "alternatives_field": "SpeechAlternatives"
    }
  ],
  "debug_metrics": false
}
```

- `worker_python` must be an absolute executable path to the isolated worker virtual
  environment. The add-on never falls back to Anki's Python runtime.
- Each mapping names a note type and its answer field. `alternatives_field` is optional; one
  explicitly accepted answer belongs on each line. Cloze note types are not eligible.
- `microphone_device_id` is a numeric PortAudio input-device ID, or `null` for the system
  default. `auto_stop_silence_ms` must be a multiple of 20 ms.
- `debug_metrics` reports timing only to stderr; it never logs recognized text or audio.

Use Anki's **Tools → Add-ons → Anki Speech Trainer → Config** editor to change this JSON. Close
and reopen the reviewer after editing it. The add-on stores neither audio nor transcripts in the
collection, notes, or its `user_files` directory.
