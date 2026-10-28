# Phase 4: Italian Practice templates and scoped speech mapping

## Implemented

- Optional `Italian Practice.apkg`, built only from a temporary collection, contains one note type,
  four native templates, shared responsive/theme-aware CSS, and an example note without learning
  history or audio.
- `Recognition`, `Speaking`, `Writing`, and `Listening` use required-field conditions on their
  complete question sides. A note can enable any subset and receives independent Anki cards.
- The worker widget mapping accepts an optional exact template name and language. `Speaking` can
  use `Target` plus `SpokenAlternatives`; other Italian Practice cards remain free of the widget.
- Existing mappings without a template name retain their original behavior. Invalid template or
  language values safely disable the affected mapping.
- A CSV validator checks immutable first-field IDs, duplicate IDs, enabled-card requirements, and
  listening sound tags without opening an Anki collection or printing learning content.

## Verified

- `just check`: 58 deterministic tests plus Ruff.
- `just validate-italian-practice`: source CSV validated.
- `just build-italian-practice` and `just verify-italian-practice`: package built from and imported
  into isolated temporary Anki collections. The verifier confirmed the imported note type, field
  order, and four templates.
- `just verify-italian-practice-integration`: imported real `Speaking`, `Writing`, and
  `Recognition` cards were checked through Anki 26.09.3's `card.template()["name"]` API; only
  `Speaking` received the configured mapping and its mapping language overrode the global default.
- `just verify-italian-practice-csv-reimport`: the source CSV was imported twice into an isolated
  collection after package installation. Its unchanged first-field IDs updated the existing note
  rather than duplicating it.

## Explicit limitation

Current Anki package import does not reliably remap static template deck-override IDs to a
receiving collection. The package therefore contains no overrides. The user assigns the four
documented overrides once after import. This is intentional and avoids stale IDs or hidden
collection writes by the add-on.

The package is not a native Cloze implementation, does not create audio, and does not provide
pronunciation scoring. It remains compatible with the existing external worker, local-only data
processing, and manual Anki review flow.
