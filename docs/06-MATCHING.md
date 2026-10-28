# 06 — Textvergleich Italienisch

## Grundprinzip

Faster-Whisper beantwortet nur „Welcher Text wurde vermutlich gesagt?“, **nicht** „Wie gut war die Aussprache?“. Der Vergleich kann falsch-negativ und falsch-positiv sein. Daher reine Textindikatoren und keine Anki-Scheduler-Automatik.

## Eingaben

- `transcript`: Rohtext der STT-Engine.
- `expected`: Inhalt des gemappten Antwortfelds (Plaintext, explizit aus der Notiz).
- `alternatives`: optionales Feld mit **einer akzeptierten Antwort pro Zeile**. Nie aus dem Deutschen automatisch übersetzen.

## Normalisierung (deterministisch, testbar)

1. Unicode NFC; Whitespace vereinheitlichen, vorne/hinten trimmen.
2. Für Groß-/Kleinschreibung `casefold()`.
3. Typografische Apostrophe (`’`, `‘`, `ʼ`) zu ASCII-Apostroph normalisieren.
4. Satzzeichen an Wortgrenzen tolerieren (`!?. ,;:`), aber keine Wörter und **keine inneren Apostrophe** löschen.
5. Akzente **nicht** entfernen: `e` und `è` können unterschiedliche Wörter sein.
6. Keine automatischen Artikel, Präpositionen oder Endungen ergänzen/entfernen; `casa` ist nicht automatisch `la casa`.
7. Keine semantischen Ähnlichkeiten oder Levenshtein-Fuzzy-Toleranz für positive Treffer; z. B. `casa` ≠ `cosa`.
8. Mehrere Spaces und Satzabschlusspunkte dürfen keinen Falschfehler verursachen.

## Bewertung

- `match` = normalisiertes Transkript entspricht einer akzeptierten normalisierten Antwort.
- `mismatch` = es wurde Sprache erkannt, aber keine Übereinstimmung gefunden.
- `uncertain` = unbrauchbare/zu kurze Audioaufnahme, niedrige Verlässlichkeit oder keine Sprache.
- `error` = technischer Fehler (Mikrofon/Worker/Modell).

Die UI muss `Erkannt: ...`, `Erwartet: ...` (ggf. erst nach Aufdecken; siehe UX) und den Ergebnisstatus getrennt anzeigen. Keine Prozentanzeige für „Aussprache“.

## Mehrdeutigkeit / Didaktik

Wenn ein deutsches Wort mehrere passende italienische Übersetzungen hat, müssen diese als Alternativen hinterlegt sein. Beispiel `das Haus` → `la casa` und `casa` nur dann beide akzeptieren, wenn im Lehrziel beide als korrekt gelten. Bei kurzen Funktionswörtern und Zahlen können STT-Fehler häufig sein: kein automatisches Negativease.

## Testfälle

`fixtures/italian-cases.json` ist die Basis. Tester müssen ausdrücklich die verschiedenen Akzente, Apostrophe, Artikel und kurze Verwechslungswörter abdecken.
