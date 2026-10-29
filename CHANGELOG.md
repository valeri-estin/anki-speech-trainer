# Changelog

## 0.1.1

- Centralized visible add-on copy, made English the default interface language,
  and added German as the optional `ui_language` translation.

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Changed

- Speaking templates now provide a touch-friendly **I can't speak right now**
  fallback that expands Anki's native typed-answer input on the same card,
  including after sync to mobile clients.
- Replaced the short licensing notice with the complete AGPL-3.0 license text
  in the repository and distributable archive.
- Replaced public, local-machine details with portable documentation and
  consolidated the active documentation in English.
- Documented dependency auditing, trusted model provisioning, and offline
  operation for public releases.

### Added

- Neutral `Language Practice` source package with `TargetLanguageText` and `Translation`, plus
  README, setup-guide, and AnkiWeb instructions for the language-deck setup assistant.
- A reproducible minimal `.ankiaddon` builder and installation guide. The
  archive excludes local `meta.json`, virtual environments, caches, and model
  data.
- An optional Italian Practice package with isolated package verification.
- A language setup assistant that previews its collection changes before a
  separate confirmation.

## 0.1.0 — 2026-10-28

- Initial local Faster-Whisper worker, bounded microphone/VAD capture, and
  conservative transcript comparison for explicitly mapped Anki review cards.
- No automatic Anki grading, no cloud service, no persisted audio, and no
  persisted transcript.
