"""Deterministic, conservative comparison for configured Italian answers."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

MatchStatus = Literal["match", "mismatch", "uncertain"]
_APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "ʼ": "'"})
_EDGE_PUNCTUATION = re.compile(r"(^|\s)[!?. ,;:]+|[!?. ,;:]+(?=\s|$)")


@dataclass(frozen=True)
class Comparison:
    """A display-safe comparison result; it never assigns an Anki grade."""

    status: MatchStatus
    normalized_transcript: str
    normalized_answers: tuple[str, ...]


def normalize(text: str) -> str:
    """Normalize harmless formatting differences while preserving Italian meaning."""
    value = unicodedata.normalize("NFC", text).translate(_APOSTROPHES).casefold()
    value = re.sub(r"\s+", " ", value).strip()
    value = _EDGE_PUNCTUATION.sub(lambda match: match.group(1) or "", value)
    return re.sub(r"\s+", " ", value).strip()


def accepted_answers(expected: str, alternatives: Iterable[str] = ()) -> tuple[str, ...]:
    """Return non-empty normalized configured answers, in stable unique order."""
    candidates = (expected, *alternatives)
    unique: dict[str, None] = {}
    for candidate in candidates:
        value = normalize(candidate)
        if value:
            unique[value] = None
    return tuple(unique)


def compare(transcript: str, expected: str, alternatives: Iterable[str] = ()) -> Comparison:
    """Compare only exact normalized strings; blank data is deliberately uncertain."""
    normalized_transcript = normalize(transcript)
    answers = accepted_answers(expected, alternatives)
    if not normalized_transcript or not answers:
        return Comparison("uncertain", normalized_transcript, answers)
    status: MatchStatus = "match" if normalized_transcript in answers else "mismatch"
    return Comparison(status, normalized_transcript, answers)
