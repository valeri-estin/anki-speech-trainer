# 14 — Referenzen (Stand 28.10.2026)

Diese Quellen sind technische Startpunkte. Vor Implementierung APIs gegen die tatsächlich installierte Anki-Version prüfen.

## Anki (offiziell)

- Add-on-Entwicklung: https://docs.ankiweb.net/addons/intro
- Hook-Dokumentation: https://docs.ankiweb.net/addons/hooks-and-filters
- Review-JavaScript: https://docs.ankiweb.net/addons/reviewer-javascript
- Add-on-Ordner und Symlink: https://docs.ankiweb.net/addons/addon-folders
- Konfiguration / `user_files`: https://docs.ankiweb.net/addons/addon-config
- Qt / aqt.qt: https://docs.ankiweb.net/addons/qt
- Editor / lokale Umgebung: https://docs.ankiweb.net/addons/editor-setup
- Aktueller Anki-Quellcode (Hook-Signaturen prüfen): https://github.com/ankitects/anki/blob/main/qt/tools/genhooks_gui.py
- Reviewer-Laufzeit: https://github.com/ankitects/anki/blob/main/qt/aqt/reviewer.py

## Sprache / Audio

- Faster-Whisper: https://github.com/SYSTRAN/faster-whisper
- sounddevice Installation: https://python-sounddevice.readthedocs.io/en/latest/installation.html
- sounddevice API: https://python-sounddevice.readthedocs.io/
- WebRTC VAD Wheels: https://pypi.org/project/webrtcvad-wheels/
- Qt QProcess: https://doc.qt.io/qt-6/qprocess.html

## Projektannahmen

- Debian 13; tatsächliche Anki-Buildversion, Desktop-Laufzeit und Mikrofon sind zur Projekterstellung nicht ausgelesen worden.
- `base` CPU/int8 ist ein Startwert, keine Benchmark-Aussage.
- Nicht alle Referenz-URLs wurden als vollständiger Implementierungsvertrag getestet. Versionsdrift muss der Agent berücksichtigen.
