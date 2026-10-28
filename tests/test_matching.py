from __future__ import annotations

import json
from pathlib import Path

import pytest

from anki_speech_trainer.matching import accepted_answers, compare, normalize


@pytest.fixture
def italian_cases() -> list[dict[str, object]]:
    fixture = Path(__file__).parents[1] / "docs" / "fixtures" / "italian-cases.json"
    return json.loads(fixture.read_text(encoding="utf-8"))["cases"]


def test_documented_italian_comparisons(italian_cases: list[dict[str, object]]) -> None:
    for case in italian_cases:
        result = compare(case["transcript"], case["expected"], case["alternatives"])
        assert result.status == case["result"], case["id"]


def test_normalization_keeps_accents_and_inner_apostrophes() -> None:
    assert normalize("  L’È  ") == "l'è"
    assert normalize("perché") != normalize("perche")


def test_empty_alternatives_are_removed_without_substring_matching() -> None:
    assert accepted_answers("la casa", ["", " casa ", "casa"]) == ("la casa", "casa")
    assert compare("la", "la casa", ["casa"]).status == "mismatch"
