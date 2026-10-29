from __future__ import annotations

from copy import deepcopy

from anki_speech_trainer.template_migration import (
    apply_speaking_template_update,
    plan_speaking_template_update,
)


class FakeModels:
    def __init__(self, *models: dict) -> None:
        self.models = {model["name"]: model for model in models}
        self.updated: list[dict] = []

    def by_name(self, name: str) -> dict | None:
        return self.models.get(name)

    def update_dict(self, model: dict) -> None:
        self.models[model["name"]] = model
        self.updated.append(deepcopy(model))


class FakeCollection:
    def __init__(self, *models: dict) -> None:
        self.models = FakeModels(*models)


def _model(name: str = "Russian Practice") -> dict:
    return {
        "name": name,
        "flds": [{"name": "Prompt"}, {"name": "Target"}],
        "tmpls": [
            {"name": "Recognition", "qfmt": "recognition", "afmt": ""},
            {"name": "Speaking", "qfmt": "<main>{{Prompt}}</main>", "afmt": ""},
        ],
    }


def _config(**overrides: object) -> dict:
    config = {
        "ui_language": "de",
        "notetype_mappings": [
            {
                "notetype_name": "Russian Practice",
                "card_template_name": "Speaking",
                "answer_field": "Target",
            }
        ],
    }
    config.update(overrides)
    return config


def test_plan_adds_a_native_fallback_only_to_the_configured_speaking_template() -> None:
    collection = FakeCollection(_model())

    plan = plan_speaking_template_update(collection, _config())

    assert [(update.note_type_name, update.template_name) for update in plan.updates] == [
        ("Russian Practice", "Speaking")
    ]
    update = plan.updates[0]
    assert "data-ast-typed-fallback" in update.updated_question_format
    assert "{{type:Target}}" in update.updated_question_format
    assert "Ich kann gerade nicht sprechen" in update.updated_question_format
    assert collection.models.updated == []


def test_plan_skips_templates_that_already_have_a_typed_fallback() -> None:
    model = _model()
    model["tmpls"][1]["qfmt"] += "\n<details class=\"lp-typed-fallback\">{{type:Target}}</details>"

    plan = plan_speaking_template_update(FakeCollection(model), _config())

    assert plan.updates == ()
    assert plan.skipped[0].reason == "already_updated"


def test_plan_skips_missing_or_unscoped_templates_without_writing() -> None:
    collection = FakeCollection(_model())
    config = _config(
        notetype_mappings=[
            {
                "notetype_name": "Missing",
                "card_template_name": "Speaking",
                "answer_field": "Target",
            },
            {"notetype_name": "Russian Practice", "answer_field": "Target"},
        ]
    )

    plan = plan_speaking_template_update(collection, config)

    assert plan.updates == ()
    assert {skipped.reason for skipped in plan.skipped} == {
        "note_type_missing",
        "template_not_scoped",
    }
    assert collection.models.updated == []


def test_apply_updates_the_reviewed_template_and_preserves_other_templates() -> None:
    model = _model()
    collection = FakeCollection(model)
    plan = plan_speaking_template_update(collection, _config())

    result = apply_speaking_template_update(collection, plan)

    assert result.updated == (("Russian Practice", "Speaking"),)
    assert len(collection.models.updated) == 1
    assert model["tmpls"][0]["qfmt"] == "recognition"
    assert "data-ast-typed-fallback" in model["tmpls"][1]["qfmt"]
