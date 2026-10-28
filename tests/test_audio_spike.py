from __future__ import annotations

import argparse

import pytest

from scripts.audio_spike import (
    FRAME_BYTES,
    FRAME_SAMPLES,
    SpikeError,
    has_input_device,
    parse_device,
)


def test_vad_frame_constants_match_16khz_pcm16_20ms() -> None:
    assert FRAME_SAMPLES == 320
    assert FRAME_BYTES == 640


def test_input_device_detection_requires_an_input_channel() -> None:
    assert has_input_device([{"max_input_channels": 0}, {"max_input_channels": 1}])
    assert not has_input_device([{"max_input_channels": 0}])


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), ("12", 12), (None, None)])
def test_parse_device_accepts_only_numeric_nonnegative_ids(
    raw: str | None, expected: int | None
) -> None:
    assert parse_device(raw) == expected


@pytest.mark.parametrize("raw", ["-1", "default", "usb microphone"])
def test_parse_device_rejects_ambiguous_or_invalid_values(raw: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        parse_device(raw)


def test_capture_rejects_a_silence_threshold_outside_vad_frames() -> None:
    class FakeVad:
        def Vad(self, _aggressiveness: int) -> object:
            raise AssertionError("VAD must not be initialized for invalid timing")

    from scripts.audio_spike import capture_until_silence

    with pytest.raises(SpikeError, match="multiple"):
        capture_until_silence(
            object(),
            FakeVad(),
            device=None,
            silence_ms=801,
            max_seconds=12,
            speech_start_timeout_seconds=8,
        )
