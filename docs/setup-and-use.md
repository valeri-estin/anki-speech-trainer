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

The first model initialization may download the configured Whisper model. Once
the model cache is populated, the normal review path can operate offline. Test
installation and configuration first in a backed-up disposable collection.

For Italian Practice, import its optional package and map the exact
`Speaking` template to `Target` and `SpokenAlternatives`. Other cards and
the normal review flow remain unchanged.
