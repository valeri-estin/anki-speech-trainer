# 11 — Ausführungsplan für den Coding-Agenten

## Phasen

### Phase 0 — Bestandsaufnahme und Technik-Spike

- Prüfe lokale Anki-Version, deren Python/Qt-Umgebung und Pfad zum `addons21`-Ordner.
- Prüfe `sounddevice`/PortAudio-Eingabegeräte aus `.venv`.
- Schreibe ein minimales, CLI-taugliches Testprogramm, das manuell startet, mit VAD stoppt und einen kurzen italienischen Satz mit Faster-Whisper transkribiert.
- Messe Modellstart- und STT-Latenz; nenne echte Werte nur nach Lauf.
- Führe `pytest`-/`ruff`-Grundsetup ein und pinne geprüfte Worker-Abhängigkeiten.
- **Akzeptanz:** Einmalige Audio→Text-Demo ohne Anki funktioniert; bei nicht vorhandenem Mikrofon dokumentierter Blocker statt vorgetäuschter Erfolg.

### Phase 1 — Add-on-Grundgerüst

- Erzeuge `anki_speech_trainer/__init__.py`, `config.json`, `config.md`, Controller und Worker-Protokoll.
- Registriere öffentliche Review-Hooks; ohne gültiges Mapping nichts einblenden.
- Implementiere Review-Widget mit Dummy-Transkript; teste Kartenwechsel und nativen Review.
- **Akzeptanz:** Anki lädt Add-on und zeigt Widget ausschließlich für gemappte Karten; kein Einfluss auf den Scheduler.

### Phase 2 — End-to-End

- Verbinde Widget über Controller/QProcess mit Worker/Audio/VAD/Faster-Whisper.
- Implementiere `request_id`/`session_id`, Cancel/Timeout/Recovery.
- Baue konservative Textnormalisierung und explizite Varianten ein.
- **Akzeptanz:** echte Mikrofonaussage wird in aktueller Karte transkribiert und korrekt als Textübereinstimmung/Abweichung angezeigt.

### Phase 3 — Härtung und UX

- Fehlerfälle, Modellwarmhaltung, Audio-Geräteauswahl, Settings, Testmatrix, Offline-Test, Dokumentation und Build-Anleitung.
- Protokolliere reale Benchmarks. Keine ungemessene Latenzbehauptung.
- **Akzeptanz:** P0-Abnahme vollständig, P1 nach Aufwand; installierbarer Entwicklerstand.

## Sofort verwendbarer Startprompt

> Du bist mein Coding-Agent und arbeitest im Repository `anki-speech-trainer`. Lies zunächst vollständig `AGENTS.md`, `README.md` und die Dateien unter `docs/`. Implementiere **Anki Speech Trainer V1** nach den verbindlichen Anforderungen. Beginne mit Phase 0 aus `docs/11-AGENT-PLAN.md`: prüfe die lokale Anki-Version und das Mikrofon, realisiere zuerst einen isolierten Audio-/VAD-/Faster-Whisper-Technik-Spike unter Debian 13, pinne anschließend getestete Abhängigkeiten und dokumentiere Messergebnisse. Entwickle danach in kleinen, testbaren Schritten das Add-on mit einem externen Worker über QProcess/JSONL. Halte den Anki-Scheduler unangetastet, beschränke die UI auf explizit gemappte Notiztypen, verwende keine Cloud und speichere keine Audiodaten. Führe nach jedem Schritt Tests und Ruff aus, ergänze `CHANGELOG.md`, aktualisiere Doku und committe nachvollziehbar. Berichte bei technischen Blockern konkret; behaupte keine Funktion, die du nicht auf echter Hardware oder im Anki-Testprofil geprüft hast.

## Umgang mit offenen Fragen

Falls es technische Abweichungen der installierten Anki-Version gibt: zuerst gegen öffentliche Hooks und Quellcode prüfen, dann ADR ergänzen, anschließend implementieren. Keine stille Ersetzung von `QProcess` durch Shell/HTTP und keine automatische Kartenbewertung.
