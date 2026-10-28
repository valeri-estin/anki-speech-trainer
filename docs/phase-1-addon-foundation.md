# Phase 1: add-on foundation

## Implemented contract

- `anki_speech_trainer` registers only the public hooks verified in Anki 26.09.3:
  `card_will_show`, `reviewer_did_show_question`, `reviewer_did_show_answer`,
  `webview_did_receive_js_message`, and `profile_will_close`.
- The widget is inserted only for `reviewQuestion` cards with an enabled, exact note-type mapping
  and a non-empty configured answer field. Cloze notes, missing fields, and unmapped note types
  receive no widget.
- Expected text comes from `card.note()` and configured fields, is reduced to plaintext, and has
  sound tags removed. Neither `card.answer()` nor any collection write is used.
- The review state machine creates a new session ID for every card. A response whose session ID
  is stale or whose card is unmapped is ignored. Within one card session, the active configuration
  and recording request IDs are also correlated, so a cancelled earlier attempt cannot overwrite
  a later attempt. Cancel is sent when a question changes, the answer is shown, or the profile
  closes.
- The worker receives and returns bounded, version-1 UTF-8 JSONL. Its stdout is protocol-only;
  diagnostics are read from stderr and not persisted. A `QProcess` starts the fixed absolute
  worker script with a configured absolute interpreter and no shell. Configuration is sent from
  Qt's `started` signal, never while `QProcess` is still in `Starting`.
- The widget renders transcript content with JavaScript `textContent`, not HTML, and never shows
  the expected answer before normal Anki reveal. It has no keyboard shortcut and no scheduler
  action.

## Verification

- Automated: matching fixture, JSONL framing/schema/error limits, widget escaping boundary, and
  stale-session state transitions (`25 passed`).
- Runtime: imported the add-on against `/usr/local/share/anki` Anki 26.09.3's Python 3.13/Qt 6
  runtime. A direct worker launch returned a valid JSONL shutdown response.

## Manual real-profile verification

The developer reported successful completion on 2026-10-28 of the documented separate-profile
setup: the add-on was linked through Anki's actual `addons21` directory, the exact `Basic`/`Back`
mapping and absolute worker interpreter were configured, and the widget was exercised on a mapped
test card. This is manual verification; no profile data, audio, or transcript is kept in this
repository.

The following edge-case evidence remains outstanding before marking every Phase 1 acceptance
scenario complete:

1. Confirm on the same separate profile that an unmapped note type receives no widget.
2. Confirm native **Show Answer** and every ease button behave identically before and after a
   widget interaction.

No architectural deviation was made. The model process remains external and no scheduler or
collection APIs are used for mutation.
