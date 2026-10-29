# Setup and use

## Requirements

- Anki Desktop 26.09 or later on Debian 13.
- A microphone and Debian's PortAudio runtime:

  ```bash
  sudo apt install libportaudio2
  ```

- A separate local Python environment. Do not install worker packages into
  Anki's bundled Python.

Create the worker environment from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-worker.txt
```

The pinned runtime packages are `av`, `ctranslate2`, `faster-whisper`,
`numpy`, `onnxruntime`, `sounddevice`, and `webrtcvad-wheels`.
Development-only tools are listed separately in `requirements-dev.txt`.

## Install and first use

1. Run `just build-addon`.
2. In Anki Desktop, choose **Tools → Add-ons → Install from file…**, choose the
   archive in `dist/`, then restart Anki.
3. Open the add-on configuration. Set `worker_python` to the absolute path of
   your `.venv/bin/python`; never use Anki's bundled interpreter.
4. Add a valid `notetype_mappings` entry. The default configuration is
   inactive until a mapping exists.
5. Open a mapped review card, click **Sprechen**, speak the expected answer,
   inspect the transcript/match indication, and choose Anki's rating yourself.

On every current Speaking template, **Ich kann gerade nicht sprechen** expands a
native Anki typed-answer input on that same card. This does not invoke the
speech worker and synchronizes to AnkiDroid and AnkiMobile with the card
template. The target is compared with Anki's normal single-line typed-answer
comparison; `SpokenAlternatives` apply only to speech matching.

Existing note types retain their current card templates when only the add-on is
upgraded. Update their Speaking template from the current source package (or
add the documented fallback markup manually in **Manage Note Types → Cards**) to
receive the fallback. The add-on deliberately never changes a collection during
review or installation.

The first model initialization may download the configured Whisper model. Once
the model cache is populated, the normal review path can operate offline. Test
installation and configuration first in a backed-up disposable collection.

For a legacy Italian Practice deck, import its optional package and map the
exact `Speaking` template to `Target` and `SpokenAlternatives`. Other cards and
the normal review flow remain unchanged.

## Create a separate language deck

1. Download or locate `Language Practice.apkg` from the release assets or
   `templates/language-practice/` in the repository.
2. In Anki, choose **File → Import** and import that source package once into a
   backed-up disposable collection.
3. Choose **Tools → Anki Speech Trainer → Set up language deck…**.
4. Select, for example, **Italian (it)** or **Russian (ru)**. For another
   language, select **Other language …** and enter a display name plus its
   two- or three-letter Whisper code.
5. Check the confirmation preview. It lists the new `<Language> Practice` note
   type, four `<Language>::…` skill decks, and the fixed Speaking language code.
   Confirm only when all names are correct.

The action never moves cards or changes existing decks, mappings, options, or
scheduling. It does not create learning notes. Each created note type has
neutral fields such as `TargetLanguageText` and `Translation`; it does not need
a `LanguageCode` field because its language is fixed by the add-on mapping.
See `18-LANGUAGE-PRACTICE.md` for details.
