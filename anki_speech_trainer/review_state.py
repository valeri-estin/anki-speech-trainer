"""Pure reviewer state transitions, separated from Qt for deterministic tests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4


class ReviewState(StrEnum):
    IDLE = "idle"
    WORKER_STARTING = "worker_starting"
    READY = "ready"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    RESULT = "result"
    ERROR = "error"


@dataclass
class ReviewSession:
    """Tracks one card-generation and makes stale worker replies harmless."""

    session_id: str = ""
    card_id: int | None = None
    state: ReviewState = ReviewState.IDLE
    mapped: bool = False

    def begin_card(self, card_id: int, mapped: bool) -> str:
        self.session_id = f"review-{card_id}-{uuid4()}"
        self.card_id = card_id
        self.mapped = mapped
        self.state = ReviewState.IDLE
        return self.session_id

    def accepts(self, session_id: str) -> bool:
        return self.mapped and session_id == self.session_id

    def start_worker(self) -> None:
        self.state = ReviewState.WORKER_STARTING

    def worker_ready(self) -> None:
        self.state = ReviewState.READY

    def recording(self) -> None:
        self.state = ReviewState.RECORDING

    def transcribing(self) -> None:
        self.state = ReviewState.TRANSCRIBING

    def result(self) -> None:
        self.state = ReviewState.RESULT

    def error(self) -> None:
        self.state = ReviewState.ERROR

    def cancel(self) -> None:
        if self.mapped:
            self.state = ReviewState.READY
