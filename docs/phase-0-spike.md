# Phase 0: environment inventory and audio feasibility spike

Checked on 2026-10-28 from this repository checkout.

## Verified local runtime

| Component | Result |
| --- | --- |
| Anki | `26.09.3` (`/usr/local/bin/anki`) |
| Anki runtime | bundled Python 3.13 and Qt 6; `aqt.qt.QProcess` is available |
| Verified public hook signatures | `reviewer_did_show_question(card)`, `reviewer_did_show_answer(card)`, `card_will_show(text, card, kind)`, and `webview_did_receive_js_message(handled, message, context)` |
| Add-on directory | `/home/valeri/.local/share/Anki2/addons21` |
| Worker runtime | repository `.venv/bin/python`, Python 3.13.5 |
| PortAudio runtime | `libportaudio2 19.6.0-1.2+b3` |
| Worker imports | sounddevice 0.5.6, webrtcvad-wheels 2.0.14.post1, Faster-Whisper 1.2.1, CTranslate2 4.8.4, NumPy 2.5.4 |
| Model cache | local Hugging Face cache has Faster-Whisper `base` snapshots |

The cached `base` model initialized in **340 ms** with CPU `int8` during this check. This is only
a warm local model-load measurement; it excludes recording and transcription, and is not an
end-to-end latency claim.

## Audio hardware blocker

The current execution session has no accessible `/dev/snd`; `arecord -l` reports no sound
cards, PulseAudio/PipeWire cannot be reached, and `sounddevice.query_devices()` returns no
input device (default input ID `-1`). Therefore the required real microphone-to-text run cannot
be honestly performed here. This is an environment blocker, not a claim that the implementation
works on a physical microphone.

## Runnable spike

`scripts/audio_spike.py` is deliberately independent of Anki and uses only the worker virtual
environment. It opens the microphone only with `--record`, captures 16 kHz PCM16 mono frames,
uses WebRTC VAD with a 300 ms pre-roll and 800 ms silence stop, then transcribes in memory with
multilingual Faster-Whisper CPU/int8 and `language=it`. It never persists audio or text and never
uses an expected answer as a Whisper prompt.

On a desktop session with a microphone, run:

```bash
just spike --list-devices
just spike --record --device DEVICE_ID
```

The script prints measured model-load, recording, and transcription durations only after a real
run. No latency values are claimed until that succeeds. In the current session, `just spike
--list-devices` exits with code 2 to report the blocker.

## Architecture impact

No architecture deviation is made: the eventual Anki process will remain free of audio and ML
dependencies, with these libraries running solely in a persistent worker. Phase 1 can proceed
with deterministic mocked worker messages; physical end-to-end acceptance remains pending a
desktop session with a visible microphone.
