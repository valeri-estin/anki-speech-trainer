# 10 — Testplan und Qualitätssicherung

## Automatisierte Tests (pytest, vollständig ohne echtes Anki/Whisper)

1. **Normalisierung:** Casefold, Unicode NFC, `l’`/`l'`, Interpunktion, Whitespace; Diakritika behalten.
2. **Alternativen:** Genau eine akzeptierte Variante reicht; leere Einträge entfernen; unerlaubte Teilstrings nicht treffen.
3. **Abweichungen:** `casa` gegen `cosa`, `e` gegen `è`, `la casa` gegen `casa` (ohne Alternative) → `mismatch`.
4. **Fehlerfälle:** Leerer Transkripttext, kein VAD, fehlendes Sollfeld, unkonfigurierter Notiztyp → kein `match`.
5. **IPC:** JSONL-Framing, mehrteilige Pipe-Reads, mehrere Nachrichten pro Chunk, Version, Größe, invalides JSON, unbekannte Nachrichtentypen.
6. **Race:** Antwort `session_id=A` nach Wechsel auf B → verworfen. Doppelte `record_start` → nicht doppelt aufnehmen.
7. **Lifecycle:** Cancel bei Karte wechseln, Add-on deaktiviert, Profilwechsel, Worker-Absturz, sauberes Beenden.
8. **XSS:** Transkript `<script>...` wird als Text angezeigt, nie als HTML interpretiert.

## Echte Integrationstests (separates Anki-Profil)

- Deutsche Vorderseite, italienische Rückseite; Kartentyp-Mapping konfigurieren.
- Original-„Antwort anzeigen“ und Ease-Buttons funktionieren ohne und mit Add-on.
- Manuell auf `Sprechen` klicken; automatisches Stoppen bei Stille; zweite Aufnahme.
- USB-Mikrofon abziehen; falsches Gerät auswählen; Worker beenden.
- Während der Verarbeitung schnell zur nächsten Karte wechseln.
- Andere Add-ons deaktiviert und danach einzeln aktiviert testen, soweit vorhanden.
- Dark Mode, Standard-Theme, Tab/Space-Keyboard, kleine Fenstergröße.
- Ohne Netzwerk mit gecachtem Modell testen.

## Italian Practice template package

- Import `templates/italian-practice/Italian Practice.apkg` into a separate profile and assign the
  documented deck overrides manually.
- Confirm one note can generate only Speaking, Speaking + Writing, Recognition + Listening, or all
  four cards based on the Enable fields.
- Confirm the widget appears only on the `Speaking` template and never exposes `Target` before
  Anki's normal answer reveal.
- Confirm a Listening card is not generated without a local `[sound:...]` tag.
- Validate the example CSV with `just validate-italian-practice`; re-importing unchanged IDs must
  update notes rather than create duplicates.
- Empty an Enable field in a disposable profile, then use Anki's **Tools → Empty Cards** flow and
  confirm that only the deliberately disabled card is offered for removal.

## Audio-Tests

Je 5 Beispiele aus vier Kategorien: Einzelwörter (z. B. `casa`), ähnliche Wörter (`casa`/`cosa`), kurze Sätze (`io sono a casa`), nicht-ideale Bedingungen (Stille/Umgebungsgeräusche). Jeweils dokumentieren: soll, erkannt, Aufnahmeende, Verarbeitungsdauer, Fehlerart. Audio nicht ohne ausdrückliche Entscheidung persistieren; im Testprotokoll nur benötigte Textbeispiele.

## Kommandos (nach Agent-Implementierung)

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
```

Die erste Iteration darf nicht allein wegen fehlender Integrationstests als „fertig“ gelten. Ein realer End-to-End-Durchlauf im Anki-Testprofil ist Pflicht.

## Abnahme-Checkliste

- [ ] P0 aus `02-SCOPE-ACCEPTANCE.md` alle erfüllt
- [ ] Alle automatisierten Tests grün
- [ ] Realer Mikrofon-Test auf Debian 13
- [ ] Normaler Anki-Review unverändert
- [ ] Offline-Test mit warmem Modell erfolgreich
- [ ] Dokumentierte, reproduzierbare Installation
- [ ] `CHANGELOG.md` aktualisiert
