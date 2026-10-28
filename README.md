# Anki Speech Trainer — Projektstart

**Status:** Spezifikation/Starterpaket, noch **kein funktionsfähiges Anki-Add-on**.
**Zielplattform für V1:** Anki Desktop auf Debian 13. **Startsprache:** Italienisch (`it`).
**Modus:** Lokal/offline nach einmaligem Download des Whisper-Modells.

## Zweck

Beim Wiederholen einer passenden Anki-Karte soll der Lernende die italienische Antwort laut sagen können. Ein separater lokaler Prozess nimmt die Stimme auf, beendet die Aufnahme nach einer Sprechpause, transkribiert sie mit Faster-Whisper und vergleicht den erkannten Text konservativ mit den hinterlegten Antworten. Die regulären Anki-Bewertungsbuttons bleiben maßgeblich.

Die Anwendung bewertet **nicht** die Aussprachequalität. STT-Ausgaben sind keine zuverlässigen Lautbewertungen.

## Lese-Reihenfolge für Coding-Agenten

1. `AGENTS.md` (verbindliche Arbeitsregeln)
2. `docs/README.md` (Index)
3. `docs/01-PRODUCT.md`, `docs/02-SCOPE-ACCEPTANCE.md`
4. `docs/03-ARCHITECTURE.md`, `docs/04-ANKI-INTEGRATION.md`, `docs/05-AUDIO-PIPELINE.md`
5. Restliche Dokumente inklusive Tests und Entscheidungen.

## Geplante Struktur nach Implementierung

```
anki-speech-trainer/
├── AGENTS.md
├── CHANGELOG.md
├── README.md
├── docs/
├── anki_speech_trainer/       # direkt als Anki-Add-on ladbares Python-Paket
│   ├── __init__.py
│   ├── config.json
│   ├── config.md
│   ├── controller.py
│   ├── review_ui.py
│   ├── matching.py
│   └── worker/
│       ├── main.py
│       ├── audio.py
│       ├── transcriber.py
│       └── protocol.py
├── tests/
└── .venv/                    # lokal, nicht versionieren
```

Die Ordner `anki_speech_trainer/` und `tests/` **werden vom Coding-Agenten erstellt**. Keine importierbare Scheinimplementierung vorgeben.

## Schnellstart

Siehe `docs/09-SETUP-DEBIAN13.md`. Ein Agent kann mit dem Prompt aus `docs/11-AGENT-PLAN.md` starten.

## Grenzen

Keine Android-Unterstützung in V1, keine Aussprachebewertung, keine automatische Scheduler-Manipulation, kein Cloud-STT, keine Speicherung der Sprachaufnahmen.
