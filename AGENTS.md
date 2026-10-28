# AGENTS.md — verbindliche Arbeitsanweisung

Du entwickelst **Anki Speech Trainer V1**, ein Anki-Desktop-Add-on für lokales aktives Sprechen, **kein eigenständiges Karteikartensystem**.

## Vor jeder Änderung
1. Lies `README.md` und **alle** Dateien in `docs/` einschließlich ADRs, Tests und Beispielen; dokumentiere Unklarheiten als ADR, statt stille Annahmen zu treffen.
2. Überprüfe die auf dem Rechner tatsächlich installierte Anki-Version und Python-Laufzeit. Gleiche verwendete Anki-Hooks gegen die **installierte** Version ab.
3. Arbeite nach `docs/11-AGENT-PLAN.md`; implementiere erst einen ausführbaren Technik-Spike (Mikrofon, VAD, STT), dann die Anki-Integration.
4. Bewahre bestehende Anki-Decks, Notiztypen, Templates, Medien und Scheduler-Zustände. Keine direkten Datenbankmanipulationen.

## Architekturvorgaben
- Das Anki-Modul nutzt nur Ankis vorhandene Python-/Qt-Umgebung und Standardbibliothek, insbesondere `aqt`, `aqt.qt`, `gui_hooks` und `QProcess`.
- Schwere Abhängigkeiten (`faster-whisper`, `ctranslate2`, `sounddevice`, `webrtcvad-wheels`, NumPy) laufen **nur** im separaten lokalen Worker über `.venv/bin/python` (oder konfigurierbaren Interpreter).
- Ein **einziger langlebiger Workerprozess** wird nach Bedarf gestartet. Keine neue Model-Initialisierung pro Karte.
- Mikrofon nur durch expliziten Klick aktivieren; danach automatisch bei Sprachpause stoppen. Bei Kartenwechsel/Anki-Ende Aufnahme abbrechen, laufende Rückgaben verwerfen.
- Worker-Transport: versionierte JSON-Lines auf stdin/stdout, kein Netzwerkserver. stdout ausschließlich maschinenlesbare Protokollnachrichten; Diagnose auf stderr.
- UI-Thread bleibt frei. Worker-Fehler dürfen die Anki-Lernfunktion nicht beeinträchtigen.
- Ausschließlich konfigurierte Notiztypen/Felder; niemals alle Karten pauschal verändern.
- Kein automatisches Anki-`Again/Hard/Good/Easy` und kein eigenmächtiges `showAnswer` in V1.
- Konservativer Textvergleich; keine Semantik-/Aussprache-Scores aus Whisper-Audio erfinden.
- Keine Audioaufnahmen oder Transkripte persistieren; keine Telemetrie; lokale Verarbeitung.

## Qualität und Lieferung
- Kleine, nachvollziehbare Arbeitsschritte. Je Schritt Testlauf, ggf. Screenshot/kurze Handprüfung, dann Commit.
- Jede nutzerrelevante Änderung bekommt einen Eintrag in `CHANGELOG.md` unter `Unreleased`.
- Unit-Tests für Normalisierung, Varianten, Zustandswechsel und Worker-Protokoll. Integrationstests anhand eines **separaten Anki-Testprofils**.
- Nutze `ruff` und `pytest`. Versionsabhängige API-Nutzung dokumentieren.
- Code und Kommentare verständlich, UI-Texte auf Deutsch (später lokalisierbar).
- Erstelle keine Builds, die Modellgewichte oder `.venv/` mit einpacken.
- Kein `git push` ohne konfiguriertes Nutzer-Remote; bei vorhandenem Remote erst nach erfolgreichen Tests pushen.
- Keine Shell-Kommandos, die Ankis Produktivdaten überschreiben oder löschen.

## Definition of Done
Siehe `docs/02-SCOPE-ACCEPTANCE.md` und `docs/10-TESTPLAN.md`. Dokumentation bei Abweichungen synchron aktualisieren.
