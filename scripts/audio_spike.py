#!/usr/bin/env python3
"""Explicit, local-only microphone → VAD → Faster-Whisper feasibility spike.

This script deliberately has no Anki imports and persists neither audio nor
transcripts. It is a developer tool: recording starts only with ``--record``.
"""

from __future__ import annotations

import argparse
import collections
import sys
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

SAMPLE_RATE = 16_000
FRAME_MS = 20
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1_000
FRAME_BYTES = FRAME_SAMPLES * 2


class SpikeError(RuntimeError):
    """A safe, actionable failure from the local feasibility spike."""


@dataclass(frozen=True)
class Recording:
    """In-memory PCM captured only after the user requested recording."""

    pcm: bytes
    duration_ms: int


def require_dependencies() -> tuple[object, object, object, object]:
    """Load heavyweight worker dependencies lazily and report setup errors."""
    try:
        import numpy
        import sounddevice
        import webrtcvad
        from faster_whisper import WhisperModel
    except ImportError as exc:  # pragma: no cover - depends on local setup
        raise SpikeError(
            "Worker dependencies are missing. Install requirements-worker.txt "
            "in the project's .venv."
        ) from exc
    return numpy, sounddevice, webrtcvad, WhisperModel


def parse_device(value: str | None) -> int | None:
    """Accept an explicit numeric device ID; avoid ambiguous device names."""
    if value is None:
        return None
    try:
        device_id = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--device must be a numeric input device ID") from exc
    if device_id < 0:
        raise argparse.ArgumentTypeError("--device must not be negative")
    return device_id


def has_input_device(devices: object) -> bool:
    """Return whether sounddevice reported a usable input channel."""
    return any(device["max_input_channels"] > 0 for device in devices)


def capture_until_silence(
    sounddevice: object,
    vad_factory: object,
    *,
    device: int | None,
    silence_ms: int,
    max_seconds: int,
    speech_start_timeout_seconds: int,
) -> Recording:
    """Capture 16 kHz mono PCM until speech is followed by a bounded pause."""
    if silence_ms < FRAME_MS or silence_ms % FRAME_MS:
        raise SpikeError(f"silence_ms must be a multiple of {FRAME_MS} ms")

    vad = vad_factory.Vad(2)
    preroll = collections.deque(maxlen=15)  # 300 ms at 20 ms/frame
    frames: list[bytes] = []
    silence_frames = 0
    started = False
    deadline = time.monotonic() + speech_start_timeout_seconds
    max_frames = max_seconds * 1_000 // FRAME_MS

    try:
        with sounddevice.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SAMPLES,
            dtype="int16",
            channels=1,
            device=device,
        ) as stream:
            print("Listening. Speak Italian; recording stops after silence.", file=sys.stderr)
            for _ in range(max_frames):
                raw_frame, overflowed = stream.read(FRAME_SAMPLES)
                if overflowed:
                    print("Audio overflow; continuing with the next frame.", file=sys.stderr)
                frame = bytes(raw_frame)
                if len(frame) != FRAME_BYTES:
                    raise SpikeError("Input device returned an invalid PCM frame")
                is_speech = vad.is_speech(frame, SAMPLE_RATE)
                if not started:
                    preroll.append(frame)
                    if not is_speech:
                        if time.monotonic() >= deadline:
                            raise SpikeError("No speech was detected before the start timeout")
                        continue
                    started = True
                    frames.extend(preroll)
                    continue
                frames.append(frame)
                silence_frames = silence_frames + 1 if not is_speech else 0
                if silence_frames * FRAME_MS >= silence_ms:
                    break
    except SpikeError:
        raise
    except Exception as exc:  # sounddevice exception types vary by PortAudio build
        raise SpikeError(f"Could not open or read the selected microphone: {exc}") from exc

    if not started:
        raise SpikeError("No speech was detected")
    if len(frames) == max_frames:
        raise SpikeError("Maximum recording duration reached; please use a shorter utterance")
    pcm = b"".join(frames)
    return Recording(pcm=pcm, duration_ms=len(frames) * FRAME_MS)


def transcribe(
    recording: Recording,
    whisper_model: object,
    numpy: np,
    *,
    language: str,
) -> tuple[str, int]:
    """Transcribe in-memory PCM without an expected-answer prompt or persistence."""
    samples = numpy.frombuffer(recording.pcm, dtype=numpy.int16).astype(numpy.float32) / 32768.0
    started_at = time.perf_counter()
    segments, _info = whisper_model.transcribe(
        samples,
        language=language,
        condition_on_previous_text=False,
        beam_size=1,
        vad_filter=False,
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    return text, round((time.perf_counter() - started_at) * 1_000)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-devices", action="store_true", help="print PortAudio devices and exit"
    )
    parser.add_argument("--record", action="store_true", help="explicitly activate the microphone")
    parser.add_argument("--device", type=parse_device, help="numeric PortAudio input device ID")
    parser.add_argument("--model", default="base", help="local Faster-Whisper model name or path")
    parser.add_argument("--language", default="it", help="Whisper language code (default: it)")
    parser.add_argument("--silence-ms", type=int, default=800, help="speech-pause stop threshold")
    parser.add_argument("--max-seconds", type=int, default=12, help="maximum capture duration")
    parser.add_argument(
        "--start-timeout-seconds", type=int, default=8, help="wait time for first speech"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    numpy, sounddevice, webrtcvad, whisper_model_class = require_dependencies()
    devices = sounddevice.query_devices()

    if args.list_devices:
        print(devices)
        return 0 if has_input_device(devices) else 2
    if not args.record:
        print(
            "Pass --record to explicitly activate the microphone, or --list-devices.",
            file=sys.stderr,
        )
        return 2
    if not has_input_device(devices):
        print("No PortAudio input device is available in this session.", file=sys.stderr)
        return 3
    if args.max_seconds <= 0 or args.start_timeout_seconds <= 0:
        print("Recording timeouts must be positive.", file=sys.stderr)
        return 2

    load_started_at = time.perf_counter()
    try:
        model = whisper_model_class(args.model, device="cpu", compute_type="int8")
        model_load_ms = round((time.perf_counter() - load_started_at) * 1_000)
        print(f"Model ready in {model_load_ms} ms.", file=sys.stderr)
        recording = capture_until_silence(
            sounddevice,
            webrtcvad,
            device=args.device,
            silence_ms=args.silence_ms,
            max_seconds=args.max_seconds,
            speech_start_timeout_seconds=args.start_timeout_seconds,
        )
        text, transcription_ms = transcribe(recording, model, numpy, language=args.language)
    except SpikeError as exc:
        print(f"Spike failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # model download/loading errors also need a clear, no-traceback result
        print(f"Spike failed while loading or transcribing locally: {exc}", file=sys.stderr)
        return 1

    print(f"Transcript: {text}")
    print(f"Recording duration: {recording.duration_ms} ms", file=sys.stderr)
    print(f"Transcription: {transcription_ms} ms", file=sys.stderr)
    return 0 if text else 4


if __name__ == "__main__":
    raise SystemExit(main())
