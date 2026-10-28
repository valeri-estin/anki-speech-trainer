from __future__ import annotations

import pytest

from anki_speech_trainer.worker.protocol import (
    MAX_MESSAGE_BYTES,
    REQUEST_TYPES,
    RESPONSE_TYPES,
    LineBuffer,
    ProtocolError,
    decode_line,
    encode,
)


def test_round_trip_request() -> None:
    encoded = encode("configure", "request-1", "session-1", {"language": "it"})
    decoded = decode_line(encoded.rstrip(b"\n"), allowed_types=REQUEST_TYPES)
    assert decoded.type == "configure"
    assert decoded.payload == {"language": "it"}


def test_line_buffer_handles_split_and_batched_pipe_reads() -> None:
    first = encode("status", "a", "session", {"state": "ready"})
    second = encode("error", "b", "session", {"code": "busy"})
    buffer = LineBuffer()
    assert buffer.feed(first[:7]) == []
    lines = buffer.feed(first[7:] + second)
    assert [decode_line(line, allowed_types=RESPONSE_TYPES).type for line in lines] == [
        "status",
        "error",
    ]


@pytest.mark.parametrize(
    "raw",
    [
        b"not json",
        b'{"v": 2, "type": "status", "request_id": "x", "session_id": "y", "payload": {}}',
        b'{"v": 1, "type": "unknown", "request_id": "x", "session_id": "y", "payload": {}}',
        b'{"v": 1, "type": "status", "request_id": "", "session_id": "y", "payload": {}}',
    ],
)
def test_protocol_rejects_invalid_messages(raw: bytes) -> None:
    with pytest.raises(ProtocolError):
        decode_line(raw, allowed_types=RESPONSE_TYPES)


def test_protocol_rejects_oversized_unterminated_pipe_data() -> None:
    with pytest.raises(ProtocolError, match="unterminated"):
        LineBuffer().feed(b"x" * (MAX_MESSAGE_BYTES + 1))


def test_encoder_rejects_oversized_payload() -> None:
    with pytest.raises(ProtocolError, match="exceeds"):
        encode("status", "request", "session", {"state": "x" * MAX_MESSAGE_BYTES})
