# Russian Practice foundation package

`templates/russian-practice/Russian Practice.apkg` is an optional foundation
package for an agent that directly generates a Russian `.apkg`. It contains a
pre-cloned `Russian Practice` note type so the generator does not need to run
the desktop language-setup flow first.

The package has the same neutral stable field order and four native templates as
`Language Practice`: `Recognition`, `Speaking`, `Writing`, and `Listening`.
Its visible card instructions are English and target-language-neutral. The
package intentionally contains no template deck overrides, because Anki package
imports do not reliably remap their IDs into a receiving collection.

## Agent hand-off

Give the deck-generating agent these three files:

1. `_vault/Learnings/Anki deck creation agent guide.md`
2. `anki_interactive_cards/templates/aic-foundation/AIC Foundation.apkg`
3. `templates/russian-practice/Russian Practice.apkg`

The agent imports both foundation packages into a temporary collection, keeps
their note types and templates unchanged, creates the requested notes, removes
every foundation note, and exports only the requested deck without learning
history. For Russian Practice, it must remove `ID = ru-a1-0001` (tag
`russian-practice::seed`) and the empty `Russian Practice` deck.

For Russian content, `TargetLanguageText` holds the complete Russian expression
and `Translation` holds its meaning. No per-note language-code field is needed:
the learner configures `ru` once in the type-scoped Speech Trainer mapping.

## Learner setup

The Speech Trainer mapping is global Anki add-on configuration and cannot be
embedded in an `.apkg`. To make the microphone widget appear on `Speaking`,
the learner must install and configure Anki Speech Trainer with:

```json
{
  "notetype_name": "Russian Practice",
  "card_template_name": "Speaking",
  "language": "ru",
  "answer_field": "Target",
  "alternatives_field": "SpokenAlternatives"
}
```

Use `Target` as the expected spoken answer and `SpokenAlternatives` for any
accepted alternatives, one per line. The worker and its local dependencies are
needed only for microphone review; the ordinary Anki card templates do not
need them.

## Rebuild and verify

Run these commands from the project root using the installed Anki runtime:

```bash
just build-russian-practice
just verify-russian-practice
```

Both commands create or import only temporary collections. The builder does
not use a personal learning profile and never includes model weights, worker
environments, media recordings, scheduling history, or local absolute paths.
