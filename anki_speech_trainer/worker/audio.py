"""In-memory audio capture, used only in the external worker process."""

from __future__ import annotations

import collections
import threading
import time
from dataclasses import dataclass

SAMPLE_RATE = 16_000
FRAME_MS = 20
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1_000
FRAME_BYTES = FRAME_SAMPLES * 2


class AudioError(RuntimeError):
    """Expected microphone, VAD, and recording-bound failure."""


@dataclass(frozen=True)
class AudioCapture:
    pcm: bytes
    duration_ms: int


def capture_speech(
    *,
    device_id: int | None,
    silence_ms: int,
    max_seconds: int,
    cancel_event: threading.Event,
    start_timeout_seconds: int = 8,
) -> AudioCapture:
    """Open a PCM16 mono stream only after record_start and stop on VAD silence."""
    if silence_ms < FRAME_MS or silence_ms % FRAME_MS:
        raise AudioError(f"silence duration must be a multiple of {FRAME_MS} ms")
    if max_seconds <= 0 or start_timeout_seconds <= 0:
        raise AudioError("recording limits must be positive")
    try:
        import sounddevice
        import webrtcvad
    except ImportError as exc:  # pragma: no cover - runtime setup failure
        raise AudioError("worker audio dependencies are unavailable") from exc

    try:
        devices = sounddevice.query_devices()
        if not any(device["max_input_channels"] > 0 for device in devices):
            raise AudioError("microphone_unavailable")
        vad = webrtcvad.Vad(2)
        pre_roll = collections.deque(maxlen=15)
        frames: list[bytes] = []
        started = False
        silent_frames = 0
        max_frames = max_seconds * 1_000 // FRAME_MS
        start_deadline = time.monotonic() + start_timeout_seconds
        with sounddevice.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SAMPLES,
            dtype="int16",
            channels=1,
            device=device_id,
        ) as stream:
            for _ in range(max_frames):
                if cancel_event.is_set():
                    raise AudioError("cancelled")
                raw, overflowed = stream.read(FRAME_SAMPLES)
                if overflowed:
                    continue
                frame = bytes(raw)
                if len(frame) != FRAME_BYTES:
                    raise AudioError("invalid_audio_frame")
                speech = vad.is_speech(frame, SAMPLE_RATE)
                if not started:
                    pre_roll.append(frame)
                    if not speech:
                        if time.monotonic() >= start_deadline:
                            raise AudioError("no_speech")
                        continue
                    started = True
                    frames.extend(pre_roll)
                    continue
                frames.append(frame)
                silent_frames = silent_frames + 1 if not speech else 0
                if silent_frames * FRAME_MS >= silence_ms:
                    break
    except AudioError:
        raise
    except Exception as exc:  # PortAudio error classes are version-specific
        raise AudioError("microphone_unavailable") from exc

    if not started:
        raise AudioError("no_speech")
    if len(frames) >= max_frames:
        raise AudioError("recording_too_long")
    return AudioCapture(pcm=b"".join(frames), duration_ms=len(frames) * FRAME_MS)
