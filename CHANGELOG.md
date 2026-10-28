# Changelog

Das Projekt orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]
### Changed
- The documented physical-desktop verification is now complete for the microphone spike, local
  test-profile add-on link, exact `Basic`/`Back` mapping, and mapped-card widget interaction.
  Local Anki-generated `meta.json` configuration is deliberately ignored because it contains
  machine-specific settings. Remaining release checks cover only explicit edge cases.
- Manual reviewer verification now also covers Cloze exclusion, cancellation on answer reveal,
  unavailable-microphone recovery, and card changes during an active speech interaction. Only
  an offline interactive run and optional additional native-control coverage remain.
- Deferred microphone selection is documented with concrete adoption criteria and a local,
  worker-isolated design, so it can be reconsidered without changing V1.

### Added
- A user-confirmed **Tools → Anki Speech Trainer → Sprach-Deck einrichten…** assistant for
  additional language practice. It previews and safely creates a language-specific `Italian
  Practice` clone, four empty skill decks, fresh deck overrides, and one template-scoped Whisper
  mapping without changing existing cards, decks, scheduler settings, media, or notes.
- Optional `Italian Practice` import package with native Recognition, Speaking, Writing, and
  Listening templates, an ID-stable CSV source example, a non-mutating source validator, and
  isolated package build/import verification.
- Template-specific mapping and language-per-mapping support. Existing note-type-only mappings
  remain compatible; the speech widget can now be constrained to `Italian Practice`/`Speaking`.
- CSV source rows now carry importable hierarchical tags, and the Italian Practice guide records
  the user-controlled FSRS/deck-settings policy.
- The source CSV now uses Anki's `#columns` directive without an accidental header-note row; a
  real isolated CSV re-import verifies that stable IDs update without duplicates.
- Repository-Starter, Architektur- und Implementierungsdokumentation für die erste lokale Version.
- Phase-0-Entwicklungsgrundlage mit gepinnten Worker-Abhängigkeiten, `just`-Workflows und einem
  lokalen Mikrofon/VAD/Faster-Whisper-Spike ohne Anki- oder Cloud-Abhängigkeit.
- Dokumentierte Laufzeit- und Hardware-Bestandsaufnahme sowie fokussierte Sicherheitsprüfung.
- Add-on-Grundgerüst mit konfiguriertem Feldmapping, namespaced Review-Widget, nicht blockierendem
  QProcess-Worker und JSONL-Protokoll; keine Scheduler- oder Collection-Änderungen.
- Deterministischer italienischer Textvergleich und automatisierte Tests für Protokoll, Race- und
  UI-Sicherheitsfälle.
- End-to-End-Workerpfad mit langlebigem lokalem Faster-Whisper-Modell, VAD-gesteuerter
  In-Memory-Aufnahme, Abbruch, Zeitgrenzen und profilweiser Prozessbereinigung.
- Controller-Tests für verworfene späte Ergebnisse und wiederherstellbare Worker-Fehler.
- Offline-Startprüfung mit lokal gecachtem Modell sowie Härtung für ungültige Worker-Konfiguration,
  parallele Aufnahmeversuche und geordnetes Beenden beim Profilwechsel.
- Worker-Konfiguration erst nach Qt-Startsignal sowie Request-Korrelation für wiederholte
  Aufnahmen derselben Karte; überlange Transkripte werden sicher begrenzt.
- Abbrechen stellt den sichtbaren Aufnahmezustand sofort wieder auf `Bereit`, auch wenn der
  Worker die Abbruchbestätigung erst später sendet.
- Qt-Start-Race beim Workerstart, späte Antworten gleicher Kartensitzungen und überschrittene
  Transkriptgrenzen abgesichert; zusätzlicher temporärer Anki-Offscreen-Starttest.
- Begrenzte Worker-Timeouts für Modellinitialisierung und Aufnahme/Transkription; späte Qt-Signale
  eines alten Workerprozesses können keinen neu gestarteten Prozess mehr beeinflussen.
- Realer Qt-QProcess-/JSONL-Smoke-Test gegen Ankis gebündelte Laufzeit; erwartete Workerbeendigung
  wird nicht mehr fälschlich als Startfehler angezeigt.
