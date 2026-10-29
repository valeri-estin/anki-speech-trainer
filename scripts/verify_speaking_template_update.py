#!/usr/bin/env python3
"""Verify the confirmed Speaking-template update in an isolated collection."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anki_speech_trainer.template_migration import (  # noqa: E402
    apply_speaking_template_update,
    plan_speaking_template_update,
)


def main() -> int:
    from anki.collection import Collection

    with tempfile.TemporaryDirectory(prefix="anki-speech-trainer-template-update-") as directory:
        collection = Collection(str(Path(directory) / "verification.anki2"))
        try:
            model = collection.models.new("Russian Practice · Verification")
            for field_name in ("Prompt", "Target"):
                collection.models.add_field(model, collection.models.new_field(field_name))
            template = collection.models.new_template("Speaking")
            template["qfmt"] = "<main>{{Prompt}}</main>"
            template["afmt"] = "{{FrontSide}}<hr id=answer>{{Target}}"
            collection.models.add_template(model, template)
            collection.models.add(model)

            config = {
                "ui_language": "de",
                "notetype_mappings": [
                    {
                        "notetype_name": "Russian Practice · Verification",
                        "card_template_name": "Speaking",
                        "answer_field": "Target",
                    }
                ],
            }
            plan = plan_speaking_template_update(collection, config)
            if len(plan.updates) != 1:
                raise ValueError("unexpected_update_plan")
            result = apply_speaking_template_update(collection, plan)
            if result.updated != (("Russian Practice · Verification", "Speaking"),):
                raise ValueError("unexpected_update_result")
            stored = collection.models.by_name("Russian Practice · Verification")
            if stored is None:
                raise ValueError("missing_note_type")
            question_format = stored["tmpls"][0]["qfmt"]
            if "data-ast-typed-fallback" not in question_format:
                raise ValueError("missing_fallback")
            if "{{type:Target}}" not in question_format:
                raise ValueError("missing_native_type_answer")
        finally:
            collection.close()
    print("Speaking template update is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
