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

## ADR-009: Kartenvorlagen-spezifisches Mapping und optionales Importpaket (accepted)
**Entscheidung:** Ein Mapping kann optional eine stabile Anki-Kartenvorlage per Name und einen
Sprachcode angeben. Das Add-on bleibt rein lesend; `Italian Practice` wird als bewusst
importierbares `.apkg` bereitgestellt, nicht beim Add-on-Start erzeugt. **Warum:** Eine einzelne
Notiz soll native Recognition-, Speaking-, Writing- und Listening-Karten mit getrennten
Wiederholungen erzeugen können, während das Widget ausschließlich bei `Speaking` erscheint.
**Konsequenz:** Legacy-Mappings ohne Kartenvorlage bleiben unterstützt. `.apkg`-Imports remappen
Deck-Override-IDs nicht zuverlässig in die Ziel-Collection; die vier Overrides werden deshalb
einmalig und ausdrücklich nach dem Import in Anki gesetzt. Das Add-on schreibt weiterhin weder
Decks, Notiztypen noch Karten.

Änderungen an akzeptierten ADRs dürfen nur mit dokumentiertem Grund erfolgen.

## ADR-010: Expliziter Assistent für weitere Sprach-Decks (accepted)
**Entscheidung:** Ein Tools-Menü-Assistent darf nach einer sichtbaren Vorschau und expliziten
Bestätigung einen neuen sprachspezifischen Klon des manuell importierten `Italian Practice`
Notiztyps, vier neue leere Skill-Decks, deren Vorlagen-Overrides und eine Speaking-Zuordnung
anlegen. **Warum:** Die manuelle Wiederholung dieser Schritte ist fehleranfällig und macht weitere
Sprachen unnötig aufwendig. **Konsequenz:** Dies ist die eng begrenzte Ausnahme zu ADR-009s
read-only Add-on-Regel. Sie betrifft nie den Reviewer/Workerpfad, existierende Karten, Notizen,
Decks, Vorlagen, Audio oder den Scheduler. Der Assistent prüft den unveränderten Ausgangstyp,
verweigert Kollisionen und räumt bei einem fehlgeschlagenen Ablauf nur eigene neue Objekte auf.
