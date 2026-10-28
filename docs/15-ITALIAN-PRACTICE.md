# Italian Practice template package

`templates/italian-practice/Italian Practice.apkg` is an optional, manually imported Anki
template package. It creates the `Italian Practice` note type and one example note. It does not
install the speech add-on, a worker runtime, model weights, or audio. Importing a package is an
explicit user action; the add-on never creates or mutates collection objects.

## Note fields

`ID` is the first field and must be permanent. It is the import identity: a CSV re-import with the
same note type and unchanged ID updates the note and preserves its review history. Do not use
Anki's internal GUID for source-managed IDs.

| Field | Purpose |
| --- | --- |
| `Prompt` | German prompt or an Italian sentence with one explicit gap. |
| `Target` | Exact Italian answer for speaking and writing. |
| `ItalianText` | Complete Italian expression or sentence for recognition and listening. |
| `TranslationDE` | Meaning of `ItalianText` shown after answer reveal. |
| `SpokenAlternatives` | Explicitly accepted spoken variants, one per line. |
| `Hint` | Optional grammatical/context hint. Do not disclose the target. |
| `AudioTarget` | Optional local Anki `[sound:filename.ext]` tag for listening. |
| `EnableRecognition`, `EnableSpeaking`, `EnableWriting`, `EnableListening` | Any non-empty value generates that skill card when its other required fields are present. |

The package uses ordinary Anki templates, not native Cloze notes. A conjugation exercise is modeled
as one independent retrieval decision, for example `Prompt = Ieri io ___ a casa.` and
`Target = sono andato`. This keeps the expected spoken/written answer unambiguous.

## Templates

| Template | Native behavior | Required fields | Intended deck override |
| --- | --- | --- |
| `Recognition` | Read Italian, recall its meaning. | `EnableRecognition`, `ItalianText`, `TranslationDE` | `Italian::Recognition` |
| `Speaking` | Read prompt, then use the local speech widget. | `EnableSpeaking`, `Prompt`, `Target` | `Italian::Speaking` |
| `Writing` | Uses Anki's native `{{type:Target}}` answer box. | `EnableWriting`, `Prompt`, `Target` | `Italian::Writing` |
| `Listening` | Hear local audio, recall its meaning. | `EnableListening`, `AudioTarget`, `ItalianText`, `TranslationDE` | `Italian::Listening` |

The Speech add-on must be configured with `card_template_name: "Speaking"`; it never displays the
widget on the other templates. It only reports a transcription match, mismatch, or uncertainty. It
does not reveal `Target`, reveal Anki's answer, grade, or navigate the reviewer.

## First-time installation

Use a separate Anki profile before importing this package.

1. In Anki, create the four decks `Italian::Recognition`, `Italian::Speaking`,
   `Italian::Writing`, and `Italian::Listening`.
2. Choose **File → Import**, select `Italian Practice.apkg`, and leave imported learning progress
   disabled. Inspect the example note after import.
3. Choose **Tools → Manage Note Types → Italian Practice → Cards**. For each named card template,
   choose **Options → Deck Override** and assign the intended deck from the table above.
4. Open the speech add-on configuration and add the exact `Speaking` mapping:

   ```json
   {
     "notetype_name": "Italian Practice",
     "card_template_name": "Speaking",
     "language": "it",
     "answer_field": "Target",
     "alternatives_field": "SpokenAlternatives"
   }
   ```

5. Close and reopen the reviewer. Test all enabled skill cards in this profile before importing
   real learning content.

Deck overrides are deliberately not embedded in the `.apkg`: current Anki package import does not
reliably remap their IDs into the receiving collection. The one-time assignment above is safe and
visible, and keeps the add-on read-only with respect to the collection.

## Additional languages

After importing and preserving the unmodified Italian source note type, choose **Tools → Anki
Speech Trainer → Sprach-Deck einrichten…**. Select a common language or enter a display name and
the Faster-Whisper language code, for example `Russisch` and `ru`. The preview names the exact
objects before confirmation:

- `Russisch Practice` as a clone of the source note type;
- `Russisch::Recognition`, `Russisch::Speaking`, `Russisch::Writing`, and
  `Russisch::Listening` as new empty decks;
- one `Russisch Practice` / `Speaking` mapping using `ru`.

The assistant sets deck overrides only on its new clone. It does not create notes or audio, move
existing cards, alter deck options, or overwrite an existing target. The inherited field name
`ItalianText` remains for schema compatibility but stores the complete text in the new target
language. The clone changes the visible Italian-specific question wording to the neutral phrase
“Zielsprache”. For a custom language, use the valid two- or three-letter code accepted by the
local Whisper worker. Do not change the Italian mapping to `ru`: keep one mapping per language.

For direct Russian deck generation without a desktop setup step, use the
pre-cloned `templates/russian-practice/Russian Practice.apkg` package instead.
Its agent and learner contract is documented in
[17-RUSSIAN-PRACTICE.md](17-RUSSIAN-PRACTICE.md).

## CSV source data

`templates/italian-practice/Italian Practice.csv` is a semicolon-separated source example. Its
Anki `#columns` directive is the schema; do not add a separate column-header data row. After the
note type is installed, validate it before import:

```bash
just validate-italian-practice
```

The validator rejects missing or duplicate IDs, no enabled card, enabled cards with missing
required fields, and Listening records without an Anki sound tag. It never opens an Anki profile,
writes data, or prints learning content. It cannot prove that an audio recording semantically
matches `ItalianText`; that remains a content-review responsibility.

The last CSV column is a special Anki tags column. Use hierarchical tags such as `niveau::A1`,
`wortart::verb`, `thema::alltag`, and `grammatik::passato-prossimo` to organize source material;
it is not an Italian Practice note field.

If an Enable field is cleared after a card has been generated, Anki does not delete the card
automatically. Review the proposed removals through **Tools → Empty Cards** in a backup/test
profile before confirming them.

## Maintaining the package

The source of truth for fields and card templates is
`anki_speech_trainer/italian_practice.py`. Rebuild and verify the binary package only with the
installed Anki runtime:

```bash
just build-italian-practice
just verify-italian-practice
just verify-italian-practice-integration
just verify-italian-practice-csv-reimport
```

The builder creates and deletes only a temporary collection. Never build a package from a personal
learning profile, and never place model weights or the worker virtual environment in the package.

## Deck and scheduling policy

The package neither creates options presets nor changes scheduler values. Configure the four skill
decks manually and use the same Anki options preset initially. A reasonable starting policy is
FSRS enabled, desired retention `0.90`, and sibling burying enabled; decide the daily new-card
limit intentionally after observing real workload. These are user-controlled deck settings, not
add-on behavior.
