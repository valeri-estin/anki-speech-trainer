"""Versioned, bounded JSON-Lines contract between Anki and the worker."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Final

PROTOCOL_VERSION: Final = 1
MAX_MESSAGE_BYTES: Final = 16_384
REQUEST_TYPES: Final = frozenset(
    {"configure", "record_start", "record_stop", "record_cancel", "shutdown"}
)
RESPONSE_TYPES: Final = frozenset({"status", "transcript", "error", "cancelled"})


class ProtocolError(ValueError):
    """A protocol violation that must not reach worker business logic."""


@dataclass(frozen=True)
class Message:
    version: int
    type: str
    request_id: str
    session_id: str
    payload: dict[str, Any]


def _validate(value: Any, *, allowed_types: frozenset[str]) -> Message:
    if not isinstance(value, dict):
        raise ProtocolError("message must be an object")
    required = {"v", "type", "request_id", "session_id", "payload"}
    if set(value) != required:
        raise ProtocolError("message fields are invalid")
    if value["v"] != PROTOCOL_VERSION:
        raise ProtocolError("unsupported protocol version")
    if value["type"] not in allowed_types:
        raise ProtocolError("unknown message type")
    if not all(
        isinstance(value[name], str) and value[name] for name in ("request_id", "session_id")
    ):
        raise ProtocolError("request_id and session_id must be non-empty strings")
    if not isinstance(value["payload"], dict):
        raise ProtocolError("payload must be an object")
    return Message(
        value["v"], value["type"], value["request_id"], value["session_id"], value["payload"]
    )


def decode_line(raw: bytes | str, *, allowed_types: frozenset[str]) -> Message:
    """Decode one bounded UTF-8 JSONL record without accepting trailing data."""
    encoded = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not encoded or len(encoded) > MAX_MESSAGE_BYTES:
        raise ProtocolError("message exceeds size limit")
    try:
        value = json.loads(encoded.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("message is not valid UTF-8 JSON") from exc
    return _validate(value, allowed_types=allowed_types)


def encode(message_type: str, request_id: str, session_id: str, payload: dict[str, Any]) -> bytes:
    """Encode a validated response/request as one UTF-8 JSONL record."""
    message = _validate(
        {
            "v": PROTOCOL_VERSION,
            "type": message_type,
            "request_id": request_id,
            "session_id": session_id,
            "payload": payload,
        },
        allowed_types=REQUEST_TYPES | RESPONSE_TYPES,
    )
    line = json.dumps(
        {
            "v": message.version,
            "type": message.type,
            "request_id": message.request_id,
            "session_id": message.session_id,
            "payload": message.payload,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(line) + 1 > MAX_MESSAGE_BYTES:
        raise ProtocolError("encoded message exceeds size limit")
    return line + b"\n"


class LineBuffer:
    """Incrementally frame bounded stdout data; supports split and batched reads."""

    def __init__(self) -> None:
        self._buffer = b""

    def feed(self, chunk: bytes) -> list[bytes]:
        if not isinstance(chunk, bytes):
            raise ProtocolError("pipe chunk must be bytes")
        self._buffer += chunk
        if len(self._buffer) > MAX_MESSAGE_BYTES and b"\n" not in self._buffer:
            self._buffer = b""
            raise ProtocolError("unterminated message exceeds size limit")
        records = self._buffer.split(b"\n")
        self._buffer = records.pop()
        output: list[bytes] = []
        for record in records:
            if record:
                if len(record) > MAX_MESSAGE_BYTES:
                    raise ProtocolError("message exceeds size limit")
                output.append(record)
        return output
