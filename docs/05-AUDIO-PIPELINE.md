# 05 — Mikrofon, VAD und Transkription

## Libraries im externen Worker

- `sounddevice`: Mikrofon/PortAudio
- `webrtcvad-wheels` (Importname `webrtcvad`): Erkennung gesprochener Sprachframes
- `faster-whisper`: Texttranskription mit CTranslate2
- `numpy`: Puffern/PCM-Konvertierung; `wave` aus stdlib für optionalen Testmodus

**V1-Default:** `WhisperModel("base", device="cpu", compute_type="int8")`, Sprache explizit auf `it` setzen. Kein `base.en` verwenden (English-only). `small` als optionale Qualitätsstufe nach Messungen. GPU bewusst nicht voraussetzen.

## Zustandsfolge

1. Worker startet, meldet `initializing` / `model_ready` (Modell nur einmal laden).
2. Nutzer startet per expliziter Aktion `record_start`; Eingabegerät öffnen.
3. PCM16-Mono in Frames (z. B. 20 ms, 16 kHz) erfassen; VAD markiert Sprachaktivität.
4. Vorlaufpuffer von ca. 200–300 ms halten, um Wortanfänge nicht abzuschneiden.
5. Nur nach tatsächlich erkannter Stimme bei ca. 700–900 ms Sprechpause stoppen; manuelles Stoppen anbieten.
6. Erfasste Äußerung an Faster-Whisper geben. Modell nach erster Initialisierung wiederverwenden.
7. Text mit `language="it"`, `condition_on_previous_text=False` (Einzeläußerungen isoliert), konservativen Decodingparametern zurückgeben.
8. Buffer nach Verarbeitung verwerfen; Eingabestream sicher schließen.

**Technikdetails:** WebRTC VAD akzeptiert nur unterstützte Sample-Rates (8000/16000/32000/48000 Hz), 16-bit Mono-PCM und 10/20/30-ms-Frames. Für 16 kHz und 20 ms: 320 Samples bzw. 640 Bytes. Falls Gerät 16 kHz nicht unterstützt, mit unterstützter Rate aufnehmen und verlustarm konvertieren; **nicht** Sample-Rate bloß umdeklarieren.

## Grenzen und Fehlverhalten

- In lärmbelasteter Umgebung kann VAD früh/spät auslösen; immer Stop-/Abbrechen-Button und konfigurierbare Silence-Dauer anbieten.
- Whisper kann auch bei Stille Wörter „halluzinieren“; deshalb Mindest-Sprachdauer, tatsächlich positives VAD und optionale no-speech-Schwelle prüfen. Kein gültiges VAD-Signal → **kein positives Bewertungsergebnis**.
- Aufnahmen zu kurz, zu lang, abgeschnitten oder verrauscht → verständliche Fehlermeldung und erneute Aufnahme.
- Versprochen wird **keine** phonetische Aussprachebeurteilung.
- Nicht Transkription mit erwarteter Lösung „primen“, sodass das Modell eine Antwort errät (keine Einfügung des Solltexts als `initial_prompt`).

## Timing / Qualitätsmessung

Messen: Zeit von Klick bis `recording`, Aufnahmeende, Whisper-Rechenzeit und Ausgabe bis UI. Metriken als anonyme Laufzeiten, ohne Audioinhalte, lokal und nur bei aktiviertem Debugging.

Minimum 20 Testäußerungen: einzelne A1-Wörter, Sätze mit 3–8 Wörtern, schwankende Sprechpausen, langsames und schnelles Sprechen, absichtliche Stille. Ziel: interaktive UI ohne Blockade und möglichst rasche Antwort, kein garantierter Zeitwert.

## Debian-Fehlersuche

PortAudio (`libportaudio2`) muss installiert sein. Test der Audiohardware mit `arecord -l` (wenn `alsa-utils` installiert ist) oder `python -c "import sounddevice as sd; print(sd.query_devices())"`. PipeWire/PulseAudio-Eingabegerät und Linux-Berechtigungen prüfen.

## Offline

Der erste Modellaufruf kann ein Whisper-Modell aus dem Internet laden. Modell vor der eigentlichen Nutzung bewusst initialisieren; spätere Laufzeit benötigt keine Cloud. Eine lokale Modellpfadangabe/Cache-Pfad konfigurieren und Offline-Test (Netzwerk aus) durchführen.
