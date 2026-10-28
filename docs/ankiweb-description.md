# AnkiWeb description

**Published add-on ID:** `717309562`  
**Release archive:** `anki-speech-trainer-0.1.1.ankiaddon`  
**Last reviewed:** 2026-10-28

Copy the content below, starting at the next heading, into AnkiWeb's
**Description** field. Keep it synchronized with the released archive.

## Local speaking practice for Anki Desktop

Anki Speech Trainer adds optional, local speech practice to selected review
cards. On a mapped card, click **Speak**, say your answer, and receive a
conservative transcript match, mismatch, or uncertainty result.

It supports active language recall, not automatic grading. Anki's normal
**Again**, **Hard**, **Good**, and **Easy** buttons remain the only scheduling
controls.

### Requirements

- Anki Desktop 26.09 or later
- Debian 13 is the currently supported and tested platform
- A working microphone
- PortAudio:

  ```bash
  sudo apt install libportaudio2
  ```

- A separate local Python environment for the speech worker. Do **not** install
  these packages into Anki's bundled Python runtime:

  ```bash
  python3 -m venv ~/anki-speech-trainer-worker
  ~/anki-speech-trainer-worker/bin/python -m pip install --upgrade pip
  ~/anki-speech-trainer-worker/bin/python -m pip install \
    av==19.0.2 \
    ctranslate2==4.8.4 \
    faster-whisper==1.2.1 \
    numpy==2.5.4 \
    onnxruntime==1.31.1 \
    sounddevice==0.5.6 \
    webrtcvad-wheels==2.0.14
  ```

The first worker start may download the selected Whisper model. Once available
locally, normal use can run offline.

### First-time setup

1. Install the add-on and restart Anki.
2. Open **Tools → Add-ons → Anki Speech Trainer → Config**.
3. Set `worker_python` to the absolute path of the worker environment's Python
   executable.
4. Add a note-type mapping for the card template and answer field you want to
   practise.
5. Close and reopen the reviewer, then test one mapped card.

Example mapping:

```json
{
  "notetype_name": "Italian Practice",
  "card_template_name": "Speaking",
  "language": "it",
  "answer_field": "Target",
  "alternatives_field": "SpokenAlternatives"
}
```

### Interface language

The interface is English by default. To use German, set this in the add-on
configuration:

```json
{
  "ui_language": "de"
}
```

Use `"en"` to switch back to English. Restart Anki or reopen the reviewer after
changing the setting.

### Daily workflow

1. Review a mapped speaking card normally.
2. Click **Speak**.
3. Speak your answer and pause.
4. Read the transcript and match result.
5. Choose **Again**, **Hard**, **Good**, or **Easy** yourself.

The transcript is learning feedback only. The add-on does not reveal answers,
rate cards, alter FSRS, or change scheduling.

### Privacy

Audio is processed locally. Recordings and transcripts are kept only temporarily
in memory and are not stored in your collection, notes, or user files. The
add-on has no cloud service or telemetry.

### License

Licensed under the GNU Affero General Public License, version 3 or later
(AGPL-3.0-or-later).

### Source code and issues

Source code, installation guidance, and issue reports are available through the
Support Page.
