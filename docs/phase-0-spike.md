# Phase 0: environment inventory and audio feasibility spike

Checked on 2026-10-28 from this repository checkout.

## Verified local runtime

| Component | Result |
| --- | --- |
| Anki | `26.09.3` |
| Anki runtime | bundled Python 3.13 and Qt 6; `aqt.qt.QProcess` is available |
| Verified public hook signatures | `reviewer_did_show_question(card)`, `reviewer_did_show_answer(card)`, `card_will_show(text, card, kind)`, and `webview_did_receive_js_message(handled, message, context)` |
| Add-on directory | Standard local Anki add-on directory (machine-specific path intentionally omitted) |
| Worker runtime | isolated Python 3.13 virtual environment |
| PortAudio runtime | Debian `libportaudio2` runtime |
| Worker imports | sounddevice 0.5.6, webrtcvad-wheels 2.0.14.post1, Faster-Whisper 1.2.1, CTranslate2 4.8.4, NumPy 2.5.4 |
| Model cache | trusted Faster-Whisper `base` snapshot provisioned locally |

The cached `base` model initialized successfully with CPU `int8`. This is a
local smoke test, not an end-to-end latency claim.

## Audio hardware availability and manual validation

The current execution session has no accessible `/dev/snd`; `arecord -l` reports no sound
cards, PulseAudio/PipeWire cannot be reached, and `sounddevice.query_devices()` returns no
input device (default input ID `-1`). Therefore the required real microphone-to-text run cannot
be honestly performed in this execution session. This remains an environment limitation of this
session, not a claim that the implementation can access its microphone.

On 2026-10-28, the developer completed the documented physical-desktop steps separately and
reported that they all worked: the device listing and explicit `--record` spike, the local add-on
symlink, the exact `Basic`/`Back` mapping, and a mapped-card widget interaction. This is manual
acceptance evidence, not a reproducible measurement from this headless execution session. No
audio or transcript was retained in the repository.

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
run. No latency values are claimed here because the reported manual run did not supply its output.
In the current execution session, `just spike --list-devices` still exits with code 2 because it
cannot access the desktop audio stack.

## Architecture impact

No architecture deviation is made: the eventual Anki process will remain free of audio and ML
dependencies, with these libraries running solely in a persistent worker. The reported desktop
run removes the original physical-microphone feasibility blocker; automated checks remain
deterministic and do not require an audio device.
