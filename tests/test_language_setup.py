from __future__ import annotations

from copy import deepcopy

import pytest

from anki_speech_trainer.language_setup import (
    LanguageSetupError,
    apply_language_setup,
    plan_language_setup,
)


class FakeDecks:
    def __init__(self, existing: set[str] | None = None) -> None:
        self.names = set(existing or ())
        self.created: dict[str, int] = {}
        self.removed: list[int] = []

    def by_name(self, name: str):
        return {"name": name} if name in self.names else None

    def id(self, name: str) -> int:
        self.names.add(name)
        identifier = len(self.created) + 100
        self.created[name] = identifier
        return identifier

    def remove(self, identifiers: list[int]) -> None:
        self.removed.extend(identifiers)


class FakeModels:
    def __init__(self, source: dict | None) -> None:
        self.source = source
        self.added: dict | None = None
        self.removed: list[int] = []

    def by_name(self, name: str):
        if self.source is not None and self.source["name"] == name:
            return self.source
        if self.added is not None and self.added["name"] == name:
            return self.added
        return None

    def copy(self, notetype: dict, add: bool = False) -> dict:
        assert notetype is self.source
        assert not add
        copied = deepcopy(notetype)
        copied["id"] = 999
        return copied

    def add_dict(self, notetype: dict) -> None:
        self.added = notetype

    def remove(self, identifier: int) -> None:
        self.removed.append(identifier)


class FakeCollection:
    def __init__(self, source: dict | None, existing_decks: set[str] | None = None) -> None:
        self.models = FakeModels(source)
        self.decks = FakeDecks(existing_decks)


class FakeAddonManager:
    def __init__(self, config: dict, fail_writes: bool = False) -> None:
        self.config = config
        self.written: dict | None = None
        self.fail_writes = fail_writes

    def getConfig(self, _addon_package: str) -> dict:
        return self.config

    def writeConfig(self, _addon_package: str, config: dict) -> None:
        if self.fail_writes:
            raise OSError("config unavailable")
        self.written = config


def _source_notetype() -> dict:
    return {
        "id": 1,
        "name": "Italian Practice",
        "flds": [
            {"name": name}
            for name in (
                "ID",
                "Prompt",
                "Target",
                "ItalianText",
                "TranslationDE",
                "SpokenAlternatives",
                "Hint",
                "AudioTarget",
                "EnableRecognition",
                "EnableSpeaking",
                "EnableWriting",
                "EnableListening",
            )
        ],
        "tmpls": [
            {"name": name, "did": None, "qfmt": "italienische Antwort", "afmt": ""}
            for name in ("Recognition", "Speaking", "Writing", "Listening")
        ],
    }


def _config() -> dict:
    return {
        "enabled": True,
        "notetype_mappings": [
            {"notetype_name": "Basic", "answer_field": "Back", "alternatives_field": ""}
        ],
    }


def test_plan_describes_new_language_without_mutating_collection() -> None:
    collection = FakeCollection(_source_notetype())

    plan = plan_language_setup(collection, _config(), "Russisch", "RU")

    assert plan.note_type_name == "Russisch Practice"
    assert plan.language_code == "ru"
    assert plan.deck_names == (
        "Russisch::Recognition",
        "Russisch::Speaking",
        "Russisch::Writing",
        "Russisch::Listening",
    )
    assert collection.decks.created == {}
    assert collection.models.added is None


@pytest.mark.parametrize(
    ("display_name", "language_code"),
    [
        ("", "ru"),
        ("Russian::Injected", "ru"),
        ("Russisch", "RUSSIA"),
        ("Russisch\nNeu", "ru"),
    ],
)
def test_plan_rejects_invalid_language_inputs(display_name: str, language_code: str) -> None:
    with pytest.raises(LanguageSetupError, match="Invalid"):
        plan_language_setup(
            FakeCollection(_source_notetype()), _config(), display_name, language_code
        )


def test_plan_refuses_to_overwrite_existing_target_objects() -> None:
    with pytest.raises(LanguageSetupError, match="Note type"):
        plan_language_setup(FakeCollection(_source_notetype()), _config(), "Italian", "it")

    with pytest.raises(LanguageSetupError, match="Deck"):
        plan_language_setup(
            FakeCollection(_source_notetype(), {"Russisch::Speaking"}), _config(), "Russisch", "ru"
        )


def test_plan_requires_the_unmodified_source_schema() -> None:
    source = _source_notetype()
    source["tmpls"] = source["tmpls"][:-1]

    with pytest.raises(LanguageSetupError, match="source note type"):
        plan_language_setup(FakeCollection(source), _config(), "Russisch", "ru")


def test_apply_creates_scoped_decks_cloned_notetype_and_exact_speech_mapping() -> None:
    collection = FakeCollection(_source_notetype())
    manager = FakeAddonManager(_config())
    plan = plan_language_setup(collection, manager.config, "Russisch", "ru")

    result = apply_language_setup(collection, manager, "anki_speech_trainer", plan)

    assert result.note_type_name == "Russisch Practice"
    assert collection.decks.created == {
        "Russisch::Recognition": 100,
        "Russisch::Speaking": 101,
        "Russisch::Writing": 102,
        "Russisch::Listening": 103,
    }
    assert collection.models.added is not None
    assert collection.models.added["name"] == "Russisch Practice"
    assert [template["did"] for template in collection.models.added["tmpls"]] == [
        100,
        101,
        102,
        103,
    ]
    assert collection.models.added["tmpls"][1]["qfmt"] == "Antwort in der Zielsprache"
    assert manager.written is not None
    assert manager.written["notetype_mappings"][-1] == {
        "notetype_name": "Russisch Practice",
        "card_template_name": "Speaking",
        "language": "ru",
        "answer_field": "Target",
        "alternatives_field": "SpokenAlternatives",
    }


def test_apply_rolls_back_only_new_objects_when_config_write_fails() -> None:
    collection = FakeCollection(_source_notetype())
    manager = FakeAddonManager(_config(), fail_writes=True)
    plan = plan_language_setup(collection, manager.config, "Russisch", "ru")

    with pytest.raises(LanguageSetupError, match="could not be completed"):
        apply_language_setup(collection, manager, "anki_speech_trainer", plan)

    assert collection.models.removed == [999]
    assert collection.decks.removed == [100, 101, 102, 103]


def test_apply_rolls_back_new_decks_when_creating_the_notetype_fails() -> None:
    collection = FakeCollection(_source_notetype())
    collection.models.add_dict = lambda _notetype: (_ for _ in ()).throw(OSError("database busy"))
    manager = FakeAddonManager(_config())
    plan = plan_language_setup(collection, manager.config, "Russisch", "ru")

    with pytest.raises(LanguageSetupError, match="could not be completed"):
        apply_language_setup(collection, manager, "anki_speech_trainer", plan)

    assert collection.models.removed == []
    assert collection.decks.removed == [100, 101, 102, 103]
