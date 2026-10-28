# 13 — Spätere Ideen (NICHT Teil von V1)

## Zurückgestellt: Mikrofon-Auswahl und -Diagnose

Die bestehende Konfiguration über `microphone_device_id` bleibt ausreichend, solange das
System-Standardmikrofon zuverlässig funktioniert. Ein eigener Auswahl-Dialog wird erst
weiterverfolgt, wenn mehrere Eingabegeräte, ein wechselndes USB-/Bluetooth-Headset oder
wiederkehrende Aufnahmefehler im Alltag auftreten.

Der spätere Zuschnitt soll bewusst klein bleiben: Der externe Worker listet Eingabegeräte per
JSONL auf, Anki zeigt nur Namen und numerische IDs, und die Auswahl wird in der Add-on-
Konfiguration gespeichert. Eine kurze Testaufnahme muss das gewählte Gerät prüfen; weder Audio
noch Transkript dürfen dafür persistiert werden. Diese Erweiterung darf weder den Anki-
Scheduler noch die Collection verändern und blockiert V1 nicht.

## V1.1

- Audiowiedergabe der eigenen Äußerung auf expliziten Klick; nur temporär im RAM, falls technische Architektur dies sauber unterstützt.
- Optionaler separater Nachsprechmodus mit bestehendem Kartenton (keine generierte TTS-Pflicht).
- Optionale manuelle Korrektur des Transkripts bei erkennbaren STT-Fehlern.
- Statusstatistik ohne Speicherung persönlicher Audiobeispiele.

## V2

- Phonem- bzw. Aussprachebewertung mit spezialisierter Engine (separater Datenschutzentscheid, eventuell Cloud).
- Optionales auto-reveal/auto-grade nur nach umfangreicher gesonderter Risikoprüfung und als explizites Opt-in.
- Sprachspezifische Normalisierungsregeln über die vorhandene Sprache-pro-Mapping-Konfiguration
  hinaus; das mitgelieferte Importpaket bleibt zunächst italienisch.
- Mobile Strategie für AnkiDroid (Desktop-Python-Add-ons laufen dort nicht direkt).
- Integriertes Gamification-Design, separate Fortschrittsleiste, Sounds und Erfolgseffekte.
- Einrichtungsassistent, Installer und signierte Distribution.

**Wichtig:** Keines dieser Features darf die Implementierung oder Abnahme von V1 blockieren.
