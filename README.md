# Anki Speech Trainer

Anki Speech Trainer is a local Anki Desktop add-on for active speaking
practice. On a configured review card, the learner can click **Sprechen** to
record an answer. An external local worker transcribes it with Faster-Whisper
and compares the transcript conservatively with the configured answer.

The add-on does not grade cards, change FSRS or scheduling, persist recordings
or transcripts, send data to a cloud service, or provide pronunciation scoring.
Anki's normal **Again**, **Hard**, **Good**, and **Easy** controls remain the
only scheduling controls.

## Requirements

- Anki Desktop 26.09 or later on Debian 13.
- A local Python virtual environment for the audio and ML worker; never install
  worker packages into Anki's bundled Python environment.
- A microphone and a configured note-type/answer-field mapping.

## Install and use

1. Create the worker environment and install dependencies:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements-worker.txt -r requirements-dev.txt
   ```

2. Run `just build-addon`. Install the generated file from `dist/` using
   **Tools → Add-ons → Install from file…**, then restart Anki.
3. In the add-on configuration, set `worker_python` to the absolute path of
   `.venv/bin/python`. Add a valid `notetype_mappings` entry. The default
   configuration is deliberately inactive until a mapping exists.
4. Open a mapped review card, click **Sprechen**, speak the answer, and read
   the transcript/match indication. Choose the regular Anki rating yourself.

For `Italian Practice`, import the optional `.apkg`, configure the mapping for
the exact `Speaking` template, `Target` answer field, and `SpokenAlternatives`
field. The normal review flow and all non-mapped cards remain unchanged.

Always test first with a backed-up disposable collection. The add-on and its
configuration are global to Anki, not isolated per collection profile.

## Development

```bash
just check
just build-addon
```

`just check` runs Ruff, the deterministic tests, and the package build. The
release archive deliberately excludes `.venv`, model weights, caches, tests,
and Anki-generated `meta.json`.

## Documentation

Read [docs/README.md](docs/README.md) for the documentation index. The most
useful operational guides are:

- `docs/09-SETUP-DEBIAN13.md` — worker and development setup
- `docs/15-ITALIAN-PRACTICE.md` — optional note-type package
- `docs/16-DISTRIBUTION.md` — archive build, installation, and configuration

## Limits

There is no AnkiDroid or iOS support in V1, no automatic rating, no cloud STT,
and no stored audio.
