# 04 — Integration in Anki

## Zielkompatibilität

Desktop-Anki auf Debian 13, zunächst **die auf dem Zielsystem installierte Anki-Version**. Verwendete Hooks bei der Implementierung in `aqt` des tatsächlich installierten Builds verifizieren; die Doku beschreibt die bevorzugten öffentlichen Schnittstellen, ist keine Versionsgarantie.

## Empfohlene Hooks

- `gui_hooks.reviewer_did_show_question(card)`: neue Review-Session; Mapping prüfen; vorherigen Aufnahmezustand invalidieren.
- `gui_hooks.reviewer_did_show_answer(card)`: laufende Aufnahme beenden, Antwortseite nicht ungewollt verändern.
- `gui_hooks.card_will_show(html, card, context)`: nur bei `context == "reviewQuestion"` einen abgegrenzten Container einfügen; nicht in Vorschau/Karteneditor und nicht für alle Karten.
- Für JS-Kommandos aus Reviewer ggf. `gui_hooks.webview_did_receive_js_message`: Nachrichten eindeutig mit `anki_speech_trainer:` prefixen und auf den Reviewer-Kontext beschränken. Rückgabesignatur der **installierten Version** prüfen.
- Für Profilwechsel und App-Shutdown die in der installierten Anki-Version vorhandenen geeigneten Hooks verwenden; bei fehlendem öffentlichen Hook kontrollierte Fallbacks dokumentieren.

## Datenzugriff

- Über `card.note()` und den **konfigurierten Feldnamen** auf die Notiz zugreifen. Niemals `card.answer()` als Rohantwort verwenden, da Backside HTML, Templates, Tondateien und TTS enthalten kann.
- Beispielschema: Notiztyp `Italienisch A1`, Felder `Deutsch`, `Italiano`, optional `SpeechAlternatives` (je Zeile eine erlaubte Alternative). Feldnamen müssen nicht exakt so heißen; Mapping ist konfigurierbar.
- Nur aktive Notiztyp-Mappings aktivieren. A mapping may additionally name one exact card-template
  name; the controller reads `card.template()["name"]`, never a template ordinal, so the widget
  can be limited to a single skill card such as `Speaking`. Older mappings without this key remain
  note-type-wide for backward compatibility. Unbekannte/fehlende Felder: Widget ausblenden oder
  klare Mapping-Fehlermeldung, keine stille Bewertung.
- In V1 **Cloze-Notiztypen ausnehmen**, da Zieltext nicht zuverlässig ohne Cloze-Kontext extrahierbar ist.
- Feldinhalt sicher in **Plaintext** umwandeln und normalisieren: Anki-Hilfsfunktionen für HTML-Bereinigung prüfen, keine untrusted HTML/JS-Injektion. Enthaltene `[sound:...]`-Tags oder Formatierung nicht als erwartete Antwort behandeln.

## Scheduler / Antworten

- Lernende bleiben in Ankis normalem Ablauf. **Keine** direkten `mw.col`-Änderungen, keine Abkürzung zu Ease-Buttons, keine direkten SQL-Zugriffe.
- Transkriptvergleich ist ein **Hinweis**, kein Scheduler-Ereignis.
- Die native Kartenrückseite wird vom Nutzer durch den normalen „Antwort anzeigen“-Mechanismus geöffnet; `Again/Hard/Good/Easy` bleiben sichtbar und funktionieren wie vorher.

## UI-Integrität

- Keinen pauschalen Monkeypatch von Ankis Reviewer-Methoden verwenden.
- Eigene DOM-IDs und CSS-Namensräume (`ast-...`) verwenden; keine globale Tastaturbelegung überschreiben.
- JS-Bridge-Nachrichten niemals aus untrusted Notiztext zusammensetzen. Ausgaben escaped als Text (`textContent`), nicht als HTML.
- CSS-Anki-Theme und Dark-Mode beachten; Widget darf andere Add-ons und normale Karten nicht überdecken.

## Lokale Entwicklerinstallation

Nach Erstellung des Anki-Pakets unter `anki_speech_trainer/` und bei geschlossenem Anki:

```bash
mkdir -p ~/.local/share/Anki2/addons21
ln -s "$(realpath anki_speech_trainer)" ~/.local/share/Anki2/addons21/anki_speech_trainer
```

Der genaue Speicherort kann je nach Installationsart abweichen. **Verlässlich ist Anki → Extras → Erweiterungen → Dateien anzeigen**. Dort die tatsächliche `addons21`-Position ablesen. Wenn der Symlink existiert, nicht blind überschreiben.

**Achtung:** Dieses Starterpaket enthält **noch kein** `anki_speech_trainer/`. Dieser Ordner wird erst durch den Coding-Agenten erzeugt.
