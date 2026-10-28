# 02 — Geltungsbereich, Abnahme

## P0 — funktionsfähiges MVP

- [ ] Add-on wird über Ankis `addons21` als Python-Paket geladen; keine Startfehler.
- [ ] Add-on lässt sich deaktivieren, ohne Karten/Notizen/Statistiken zu ändern.
- [ ] Konfiguration einer oder mehrerer Notiztyp-/Antwortfeld-Zuordnungen möglich; ohne gültige Zuordnung kein Sprech-Widget.
- [ ] Mikrofon wird nur auf expliziten Nutzerklick geöffnet; Aufnahmestatus sichtbar.
- [ ] Audio wird im separaten Worker erfasst und bei Sprecherpause gestoppt; manueller Stop und Abbrechen möglich.
- [ ] Ein lokal geladenes, **mehrsprachiges** Faster-Whisper-Modell (Default `base`, `language=it`, CPU `int8`) liefert Text zurück.
- [ ] Ergebnisse erscheinen in der aktuellen Karte; alte Ergebnisse dürfen nach Kartenwechsel **niemals** angezeigt werden.
- [ ] Vergleich mit konfiguriertem Zieltext + expliziten Varianten; Ergebnis enthält erkannte Transkription.
- [ ] Bei fehlender Hardware, verweigertem Mikrofon, Timeout, leerer Sprache, Modellfehlern oder Worker-Absturz klare Meldung und normal weiterlernbares Anki.
- [ ] Automatische Anki-Kartenbewertung ist deaktiviert bzw. nicht implementiert. Keine direkte Änderung an Collection/Scheduler.
- [ ] Tests für Normalisierung, Vergleich, Worker-Protokoll und mindestens einen simulierten Kartenwechsel.

## P1 — gute erste Version

- [ ] Modell bleibt zwischen Karten geladen; Sprechpause und Mikrofon wählbar.
- [ ] Einstellungsdialog (Sprache, Notiztyp, Antwortfeld, Alternativenfeld, Eingabegerät, Modell, Interpreterpfad).
- [ ] Status „Modell lädt“, „Bereit“, „Hört zu“, „Wird erkannt“, „Ergebnis“, „Fehler“.
- [ ] Einstellungen für optionalen Sprechmodus (nur explizite Karten/Notiztypen), deutsche UI.
- [ ] Benchmarkprotokoll: Startzeit, Modellladezeit, Erkennungsdauer und Hardware.
- [ ] Installationsanleitung für ein frisches Desktop-Anki-Testprofil.

## Explizite Nicht-Ziele

- Kein Phonem-/Aussprache-Score, kein Sprachlehrer-KI-Feedback.
- Kein Echtzeit-Streaming während des Sprechens (V1 transkribiert nach VAD-Ende).
- Kein daueraktives Lauschen, keine Hintergrundüberwachung, kein Wake-Word.
- Kein AnkiDroid, iOS, Cloud-API, Benutzerkonto oder Telemetrie.
- No automatic card/deck generation, mutation of existing notes/templates, or TTS audio
  acquisition. An optional, user-imported note-type package is allowed. A separately confirmed
  Tools-menu setup action may create a new language-specific clone, four empty skill decks, deck
  overrides, and one mapping; it must never run automatically or alter existing collection objects.
- Keine direkte Fortschrittsleiste oder Duolingo-Replik in V1; kompatible, zurückhaltende Anki-UI.
- Keine automatische Scheduler-Bewertung, keine Auto-Weiterleitung zur nächsten Karte.

## Abnahmeszenarien

| ID | Ausgangslage | Erwartung |
| --- | --- | --- |
| A01 | Gemappte Karte `Deutsch=das Haus`, `Italiano=la casa` | „La casa“: normalisiert „Text stimmt überein“ |
| A02 | Gleiche Karte, gesprochen „la cosa“ | „Text weicht ab“, kein Auto-Again |
| A03 | Normale Anki-Karte, nicht gemappter Notiztyp | Kein Widget, unveränderte Anki-Ansicht |
| A04 | Wort korrekt erkannt, Nutzer wählt „Schwer“ | Anki bewertet regulär mit „Schwer“ |
| A05 | Mikrofon fehlt | Lesbare Fehlermeldung; normale Lernbuttons bleiben nutzbar |
| A06 | Karte während Erkennung gewechselt | Ergebnis wird verworfen und nicht auf der nächsten Karte dargestellt |
| A07 | Keine Sprache | Keine hallucination-basierte positive Bewertung; Wiederholen angeboten |
| A08 | Worker beendet/Anki geschlossen | Mikrofonressourcen und Unterprozess werden freigegeben |
| A09 | Add-on deaktiviert | Sammlung/Scheduler/Notizen unverändert |

**Performance-Ziel, keine Garantie:** Bei kurzen Äußerungen auf der Zielhardware soll die gefühlte Wartezeit nach Sprechende möglichst niedrig sein. Benchmarken; wenn der Median > 2 s beträgt, erst Modellgröße, Beam-Size und Audio-Overhead prüfen. Keine unbelegte Latenzgarantie geben.
