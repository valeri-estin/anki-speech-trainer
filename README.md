# Anki Speech Trainer

Anki Speech Trainer is a local Anki Desktop add-on for active speaking
practice. On a configured review card, the learner can click **Speak** to
record an answer. An external local worker transcribes it with Faster-Whisper
and compares the transcript conservatively with the configured answer. Speaking
templates also include a native typed-answer fallback for quiet situations and
mobile review.

The add-on does not grade cards, change FSRS or scheduling, persist recordings
or transcripts, send data to a cloud service, or provide pronunciation scoring.
Anki's normal **Again**, **Hard**, **Good**, and **Easy** controls remain the
only scheduling controls.

## Requirements

- Anki Desktop 26.09 or later on Debian 13.
- The Debian runtime library `libportaudio2` for microphone access:

  ```bash
  sudo apt install libportaudio2
  ```

- A local Python virtual environment for the audio and ML worker; never install
  worker packages into Anki's bundled Python environment.
- A microphone and a configured note-type/answer-field mapping.

The required worker packages are pinned in `requirements-worker.txt`:
`av`, `ctranslate2`, `faster-whisper`, `numpy`, `onnxruntime`, `sounddevice`,
and `webrtcvad-wheels`. The first worker start may download the selected Whisper
model; later use can run offline from the local model cache. `pytest`, `ruff`,
and `pip-audit` in `requirements-dev.txt` are development-only and not required
to use the installed add-on.

## Install and use

1. Create the worker environment and install dependencies:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements-worker.txt
   ```

2. Run `just build-addon`. Install the generated file from `dist/` using
   **Tools → Add-ons → Install from file…**, then restart Anki.
3. In the add-on configuration, set `worker_python` to the absolute path of
   `.venv/bin/python`. Add a valid `notetype_mappings` entry. The default
   configuration is deliberately inactive until a mapping exists.
   The interface is English by default. Set `ui_language` to `"de"` in the
   same configuration to use German; `"en"` switches back to English.
4. Open a mapped review card, click **Speak**, speak the answer, and read
   the transcript/match indication. Choose the regular Anki rating yourself.

For an existing legacy `Italian Practice` deck, import its optional `.apkg` and
configure the mapping for the exact `Speaking` template, `Target` answer field,
and `SpokenAlternatives` field. The normal review flow and all non-mapped cards
remain unchanged.

### Create a separate language deck

For every new language, use the neutral `Language Practice.apkg` foundation
package from `templates/language-practice/` (or the matching release asset):

1. In Anki, choose **File → Import** and import `Language Practice.apkg` once.
2. Choose **Tools → Anki Speech Trainer → Set up language deck…**.
3. Select a language such as **Italian (it)** or **Russian (ru)**, or enter a
   custom display name and a two- or three-letter Whisper code.
4. Review the preview and confirm it.

The assistant creates, for example, `Russian Practice` and the four decks
`Russian::Recognition`, `Russian::Speaking`, `Russian::Writing`, and
`Russian::Listening`. It also adds the fixed `ru` speech mapping for that note
type. It never changes an existing deck, note, card, scheduler setting, or
mapping. See [`docs/18-LANGUAGE-PRACTICE.md`](docs/18-LANGUAGE-PRACTICE.md)
for the field schema and existing-Italian migration guidance.

For a direct generator creating a Russian deck, use the companion
`templates/russian-practice/Russian Practice.apkg` foundation package. It
already contains the `Russian Practice` note type; the learner must still add
its separate `Speaking` mapping with language code `ru`. See
[`docs/17-RUSSIAN-PRACTICE.md`](docs/17-RUSSIAN-PRACTICE.md).

Always test first with a backed-up disposable collection. The add-on and its
configuration are global to Anki, not isolated per collection profile.

## Development

```bash
just check
just build-addon
```

`just check` runs Ruff, the deterministic tests, and the package build. The
release archive deliberately excludes `.venv`, model weights, caches, tests,
and Anki-generated `meta.json`, and includes the project `LICENSE`.

Before a public release, install the development requirements and run
`just audit-deps`. See the
[privacy, security, and release guide](docs/privacy-security-and-release.md)
for model provenance and the complete publication checklist.

## Documentation

Read [docs/README.md](docs/README.md) for the documentation index. The most
useful operational guides are:

- `docs/09-SETUP-DEBIAN13.md` — worker and development setup
- `docs/15-ITALIAN-PRACTICE.md` — optional note-type package
- `docs/18-LANGUAGE-PRACTICE.md` — create separate language decks
- `docs/16-DISTRIBUTION.md` — archive build, installation, and configuration

## Limits

The microphone widget has no AnkiDroid or iOS support in V1. The synchronized
Speaking card template does provide its native typed-answer fallback on those
clients. There is no automatic rating, cloud STT, or stored audio.

## License

Licensed under the GNU Affero General Public License, version 3 or later
(AGPL-3.0-or-later). See [LICENSE](LICENSE).
