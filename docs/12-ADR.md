# 12 — Architecture Decision Records (festgelegt)

## ADR-001: Externer STT-Prozess (accepted)
**Entscheidung:** ML- und Audio-Libraries nur im lokalen Workerprozess. **Warum:** Isolation nativer Bibliotheken und UI-Responsivität. **Konsequenz:** IPC und separate Python-Runtime nötig.

## ADR-002: Faster-Whisper multilingual `base`, CPU int8 (accepted)
**Warum:** Funktioniert voraussichtlich auf Debian ohne NVIDIA/CUDA; auf echte CPU-Messungen folgen `tiny`/`small`-Vergleiche. **Konsequenz:** Keine Latenzgarantie, initialer Modelldownload.

## ADR-003: Mikrofon nur nach Nutzerklick, dann VAD-Stopp (accepted)
**Warum:** Transparente Aktivierung und schnelle Sprachinteraktion ohne permanente Aufnahme. **Konsequenz:** Kein Always-on, kein Wake-Word.

## ADR-004: Kein automatisches Scheduling in V1 (accepted)
**Warum:** STT kann korrekt gesprochenen Text falsch erkennen und umgekehrt. **Konsequenz:** Anki-Ease-Buttons bleiben allein maßgeblich.

## ADR-005: Feldmapping pro Notiztyp (accepted)
**Warum:** Bestehende Decks sind heterogen und `card.answer()` enthält Darstellung statt verlässlichem Solltext. **Konsequenz:** Einmalige Konfiguration notwendig; Cloze zunächst nicht unterstützt.

## ADR-006: Exakte Übereinstimmung nach begrenzter Normalisierung (accepted)
**Warum:** Fuzzy-Stringvergleich akzeptiert falsche Vokabeln (`casa` vs. `cosa`). **Konsequenz:** Freigegebene Varianten explizit speichern.

## ADR-007: JSONL über QProcess statt lokalem HTTP (accepted)
**Warum:** Keine offenen Ports, simple kontrollierbare Laufzeit. **Konsequenz:** Framing, Request-IDs, Fehlerzustände implementieren.

## ADR-008: Entwicklung über Symlink und separates Anki-Testprofil (accepted)
**Warum:** Schnelle Iteration ohne Produktivdatenrisiko. **Konsequenz:** Distribution/Installer für Worker-Runtime später.

Änderungen an akzeptierten ADRs dürfen nur mit dokumentiertem Grund erfolgen.
