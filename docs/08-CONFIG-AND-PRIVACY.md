# 08 — Konfiguration, Daten und Datenschutz

## Geplante Add-on-`config.json` (Beispiel, verbindliche Namen später implementieren)

```json
{
  "enabled": true,
  "language": "it",
  "worker_python": "",
  "model": "base",
  "device": "cpu",
  "compute_type": "int8",
  "microphone_device_id": null,
  "auto_stop_silence_ms": 800,
  "max_record_seconds": 12,
  "notetype_mappings": [
    {
      "notetype_name": "Italienisch A1",
      "answer_field": "Italiano",
      "alternatives_field": "SpeechAlternatives"
    },
    {
      "notetype_name": "Italian Practice",
      "card_template_name": "Speaking",
      "language": "it",
      "answer_field": "Target",
      "alternatives_field": "SpokenAlternatives"
    }
  ],
  "debug_metrics": false
}
```

**Sicherer Default:** Wenn kein Mapping existiert oder das Zielfeld fehlt, wird **kein** Sprechergebnis mit einer Lösung verglichen. `worker_python` wird nach lokalem Setup auf den absoluten Pfad zu `.venv/bin/python` gesetzt oder durch einen sicheren Installationsassistenten gefunden; nicht auf Ankis eigenen Interpreter zurückfallen.

`card_template_name` is optional. When it is present, only a card whose stable template name exactly
matches it receives the widget; mappings without it keep the existing note-type-wide behavior.
`language` is also optional and falls back to the top-level setting. Invalid language or template
values are treated as an inactive mapping.

## Konfiguration via Anki

`mw.addonManager.getConfig(__name__)` / `writeConfig(__name__, config)` und eine `config.md` verwenden. Zur ersten funktionsfähigen Version ist die JSON-Konfiguration ausreichend; ein kompakter Einstellungsdialog folgt als P1.

For an additional language, use **Tools → Anki Speech Trainer → Sprach-Deck einrichten…** after
importing `Italian Practice`. The dialog previews a `<Language> Practice` clone, four empty skill
decks, and the exact added mapping before a separate confirmation. It accepts a display name and a
two- or three-letter Whisper language code (for example `ru`, normalized to lowercase), refuses
collisions, and does not edit an existing mapping. It stores no audio, transcripts, or credentials.

## Datenverarbeitung

- **Lokale Mikrofonaufnahme:** nur nach Klick, nur im RAM, danach sofort freigeben.
- **Erkannter Text:** nur flüchtig im Controller/UI, keine Speicherung in Collection oder Notizfeldern.
- **Modellgewichte:** einmaliger Download aus vertrauenswürdiger Quelle in externen Cache; keine Auslieferung im Repository.
- **Diagnose:** standardmäßig nur technische Fehler ohne Sprachtext, keine Audiodateien oder Transkripte.
- **Netzwerk:** Worker erstellt keinen HTTP-Server, keine Cloud-API, kein Tracking. Offline-Tests verpflichtend.
- **Metadaten:** Konfiguration kann in Ankis Add-on-Metadaten liegen; keine Secrets vorgesehen.

## Sicherheitsregeln

`QProcess` mit festem ausführbaren Interpreter-Pfad und Argumentliste starten, **keine Shell** und keine Benutzereingaben als Shellstring. stdout-Protokoll gegen Größenüberschreitung begrenzen, Protokollfelder validieren, HTML-Text escaped ausgeben. Mikrofon bei Fehlzuständen schließen. Keine externen Audioaufnahmen aus dem Internet nachladen.

## Distribution

Das Add-on kann als `.ankiaddon` gepackt werden, die `.venv` und große ML-Gewichte jedoch **nicht**. V1 ist zunächst eine Entwicklerinstallation über lokalen Symlink. Ein Installationsassistent für den externen Worker gehört in eine spätere Distribution.
