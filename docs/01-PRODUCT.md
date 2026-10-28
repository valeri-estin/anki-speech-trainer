# 01 — Produktkonzept

## Problem

Traditionelle Anki-Karten prüfen oft passives Wiedererkennen. Beim Sprachenlernen wird jedoch zusätzlich aktives Abrufen und Sprechen benötigt. Dieses Add-on soll das Sprechen als zusätzlichen freiwilligen Schritt in die reguläre Anki-Wiederholung einbinden.

## Zielgruppe

Einzelperson, Italienisch auf A1-Niveau, Anki Desktop auf Debian 13. Andere Sprachen sind architektonisch vorzusehen, aber keine zusätzlichen UI-Modi erforderlich.

## Kern-User-Story

> Wenn ich eine entsprechend konfigurierte Karte mit deutscher Aufforderung sehe, möchte ich per Klick auf ein Mikrofon ein italienisches Wort oder einen kurzen Satz sprechen, anschließend schnell erkennen können, was verstanden wurde und ob der Text zur hinterlegten Antwort passt. Danach bewerte ich die Karte selbst mit Ankis regulären Buttons.

## Idealer Ablauf

1. Anki zeigt die Vorderseite einer **explizit freigegebenen** Karte, z. B. „das Haus“.
2. Add-on zeigt eine kleine, klar beschriftete Sprech-Komponente. Originalkarte bleibt lesbar.
3. Lernender klickt auf **Sprechen**. Der Worker aktiviert das Mikrofon, zeigt Aufnahmezustand an.
4. Die Aufnahme stoppt nach ausreichend Stille automatisch oder per Klick auf **Stoppen**.
5. Faster-Whisper erkennt „la casa“ mit festgelegter Sprache Italienisch.
6. Add-on vergleicht den erkannten Text mit dem expliziten Antwortfeld bzw. erlaubten Alternativen.
7. UI zeigt **Erkannt: la casa** und „Text stimmt überein“ oder „Text weicht ab“; bei Problemen „Nicht sicher erkannt“.
8. Der Lernende sieht über den normalen Anki-Mechanismus die Kartenrückseite und entscheidet selbst zwischen Wiederholen / Schwer / Gut / Einfach.

## Erfolgskriterien

- Vorhandene Lernkarten können unverändert weiterverwendet werden; nur eine Feldzuordnung ist nötig.
- Erkennungsfehler werden nicht mit Aussprachefehlern gleichgesetzt.
- Anki-Synchronisierung, Medien und FSRS/SM-2 bleiben unverändert.
- Normaler Lernmodus funktioniert bei Worker-Ausfall ungestört.
- Kein Cloudkonto und keine Registrierung erforderlich.

## Produktprinzipien

Freiwillig statt störend; keine Lernfortschritts-Manipulation; Geschwindigkeit vor grafischer Spielerei; klare Fehler; lokale Datenhoheit; vollständige Zugänglichkeit per Tastatur plus sichtbarer Mikrofonstatus.
