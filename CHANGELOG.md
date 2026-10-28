# Changelog

Das Projekt orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]
### Added
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

### Not implemented yet
- Das eigentliche Anki-Add-on, die Audioaufnahme, der Worker und die Tests.
