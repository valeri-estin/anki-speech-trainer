# Language Practice source package

`templates/language-practice/Language Practice.apkg` is the neutral source for
new, separate language decks. It has no per-note language code. Instead, the
setup assistant stores the selected Whisper code once in the Speaking mapping
for each language-specific note-type clone.

## Create a language deck

1. In a backed-up test collection, choose **File → Import** and import
   `Language Practice.apkg` once.
2. Choose **Tools → Anki Speech Trainer → Set up language deck…**.
3. Choose a language, such as **Italian (it)** or **Russian (ru)**. Use **Other
   language …** only when the desired language is not listed; enter its display
   name and valid two- or three-letter Whisper code.
4. Inspect the preview. For Russian it must list `Russian Practice`,
   `Russian::Recognition`, `Russian::Speaking`, `Russian::Writing`,
   `Russian::Listening`, and code `ru`.
5. Confirm the action. Add notes to the resulting `Russian Practice` type and
   place/import them into the relevant Russian decks.

The assistant never moves or edits existing cards, notes, decks, mappings,
options, media, or scheduler state. Existing target objects cause a safe error.
It also never creates learning notes; the one source example is only an
import/schema check and can be removed after the clone is created.

## Field schema

| Field | Purpose |
| --- | --- |
| `ID` | Stable source/import identity; never change it during a CSV re-import. |
| `Prompt` | Prompt in the learner's known language or an explicit sentence gap. |
| `Target` | Exact expected answer for Speaking and Writing. |
| `TargetLanguageText` | Complete expression/sentence in the language being learned. |
| `Translation` | Meaning shown after answer reveal. |
| `SpokenAlternatives` | Explicitly accepted Speaking variants, one per line. |
| `Hint` | Optional retrieval hint that does not reveal the target. |
| `AudioTarget` | Optional local Anki `[sound:filename.ext]` tag for Listening. |
| `EnableRecognition`, `EnableSpeaking`, `EnableWriting`, `EnableListening` | Non-empty values create the matching native skill cards. |

`LanguageCode` is deliberately not a field. `Italian Practice` and `Russian
Practice` are separate note types, so their respective `it` and `ru` mapping is
unambiguous even when cards are interleaved in review.

## Quiet and mobile fallback

Speaking cards include an **Ich kann gerade nicht sprechen** control that expands
Anki's native `{{type:Target}}` input on the same card. It does not start the
desktop speech worker and therefore works after sync in AnkiDroid and AnkiMobile
as well. The typed comparison is against the single `Target` value; accepted
speech-only alternatives are not used for that comparison.

## Existing Italian Practice package

The older `Italian Practice` package is retained for compatibility and uses
`ItalianText`/`TranslationDE`. It remains usable with its existing mapping. Do
not rename those fields in an existing learning collection: Anki schema changes
can require a note-type migration. If it contains no valuable cards, remove its
example note/type manually in a backup and start fresh with `Language Practice`.
The setup assistant intentionally never performs this destructive migration.
