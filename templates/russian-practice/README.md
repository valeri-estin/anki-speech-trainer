# Russian Practice foundation package

`Russian Practice.apkg` is a foundation package for a direct Anki deck generator.
It creates the `Russian Practice` note type with the native `Recognition`,
`Speaking`, `Writing`, and `Listening` templates. It contains one seed note with
`ID = ru-a1-0001` and the tag `russian-practice::seed`; it has no learning
history, media, worker, model weights, or speech-recognition configuration.

Use it together with [the deck creation agent guide](../../../_vault/Learnings/Anki%20deck%20creation%20agent%20guide.md)
and `AIC Foundation.apkg` when an agent must generate a complete Russian `.apkg`.

## Direct generator contract

1. Import `Russian Practice.apkg` into a temporary collection.
2. Preserve the `Russian Practice` note type and its four templates exactly.
3. Add the generated Russian notes to the requested deck hierarchy.
4. Remove the seed note `ID = ru-a1-0001` (or tag `russian-practice::seed`) and
   the now-empty `Russian Practice` deck before final export.
5. Export the requested deck without scheduling history, absolute paths, or
   foundation notes.

The inherited field names `ItalianText` and `TranslationDE` are stable schema
identifiers. For this Russian note type, store complete Russian text in
`ItalianText` and its German meaning in `TranslationDE`; do not rename either
field.

The foundation does not configure the speech widget. On the learner's Anki
Desktop installation, Anki Speech Trainer needs this exact mapping:

```json
{
  "notetype_name": "Russian Practice",
  "card_template_name": "Speaking",
  "language": "ru",
  "answer_field": "Target",
  "alternatives_field": "SpokenAlternatives"
}
```

The worker, microphone, and add-on are not required to generate or import the
package. They are required only for the **Speak** widget during review.
