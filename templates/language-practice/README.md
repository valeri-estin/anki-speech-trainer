# Language Practice source assets

This directory contains the neutral source package used by **Tools → Anki
Speech Trainer → Set up language deck…**. Import `Language Practice.apkg` once,
then use that menu action to create a separate note-type clone, four skill decks,
and one fixed speech-language mapping for each language.

The source package is not itself a learning deck. Do not add production content
to it or rename its fields/templates: the setup assistant validates this schema
before it creates a language clone.

The stable fields are `TargetLanguageText` for the complete expression in the
language being learned and `Translation` for its meaning. No per-note
`LanguageCode` field exists: each clone has its selected Whisper language code
stored once in the add-on mapping.

Rebuild and verify from the repository root:

```bash
just validate-language-practice
just build-language-practice
just verify-language-practice
just verify-language-setup
```
