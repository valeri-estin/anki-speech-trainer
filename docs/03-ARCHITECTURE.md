# 03 — Softwarearchitektur

## Struktur

```
Anki Desktop / aqt (Hauptprozess, GUI-Thread)
  ├─ Hook-Registrierung / Konfiguration
  ├─ ReviewController (Zustandsautomat)
  ├─ UI-Integration in Reviewer (HTML/CSS/JS + Bridge)
  ├─ answer_matcher (pure Python, unit-testbar)
  └─ QProcess JSONL Client (nicht blockierend)
       │ stdin/stdout: 1 JSON pro Zeile, kein Netzwerk
       ▼
Worker (.venv/bin/python worker/main.py)
  ├─ Audio Capture: sounddevice/PortAudio
  ├─ VAD: webrtcvad-wheels + begrenzte Frames
  ├─ Faster-Whisper: lang=it, device=cpu, compute_type=int8
  └─ JSONL Dispatcher / Error Handling
```

## Warum zwei Prozesse?

Anki bringt eine eigene Python-/Qt-Umgebung mit. `ctranslate2` und PortAudio-Abhängigkeiten im Anki-Prozess können Startprobleme verursachen. Ein dedizierter Worker isoliert Audio, ML und deren native Bibliotheken. `QProcess` ist in Qt vorhanden und erlaubt nicht blockierendes Lesen/Schreiben.

## Komponentenvertrag

- **Anki-Adapter:** Initialisiert Hooks, liest gemappte Felder und optional einen exakten
  Kartenvorlagen-Namen, hält aktive Karte/Profil fest; niemals eigene Scheduler-Operationen.
- **Language Setup:** Ein ausschließlich über das Tools-Menü nach Vorschau und Bestätigung
  ausgelöster Dialog. Er klont den geprüften Ausgangsnotiztyp, erstellt vier neue leere Skill-Decks,
  setzt nur beim Klon deren Deck-Overrides und ergänzt genau eine Speaking-Zuordnung. Der
  Review-/Workerpfad ruft diese Komponente nie auf.
- **ReviewController:** Verwaltet `idle → worker_starting → ready → recording → transcribing → result|error`; setzt beim Kartenwechsel `session_token` neu. Nur er ändert den sichtbaren Status.
- **Renderer:** Darstellung in der Review-Frageseite. Darf keine Worker-Logik enthalten; JS sendet nur namespacete UI-Kommandos an Python, falls die Bridge verwendet wird.
- **WorkerClient:** Startet den Worker mit konfiguriertem Interpreter und Absolutpfad auf das Skript, verwaltet Protokoll, Puffer und Worker-Lebenszeit.
- **AudioWorker:** Erfasst PCM16-Mono, kontrolliert Start/Stop, führt VAD und Whisper aus, gibt keine UI-Updates direkt an Anki.
- **Matcher:** `compare(transcript, accepted_answers) -> status + normalized_text`, ohne I/O und ohne Side Effects.

## IPC: JSON Lines Version 1

Alle Nachrichten sind UTF-8 und mit `\n` abgeschlossen. Jede Anfrage erhält `request_id` und `session_id`. Das UI verwirft Nachrichten mit unbekannter oder veralteter Session. stdout enthält **ausschließlich** Protokollnachrichten; Debug-Ausgabe erfolgt auf stderr (ohne Textinhalt).

Beispiel Python → Worker:

```json
{"v":1,"type":"configure","request_id":"c1","session_id":"review-42","payload":{"language":"it","model":"base","device":"cpu","compute_type":"int8"}}
{"v":1,"type":"record_start","request_id":"r1","session_id":"review-42","payload":{"device_id":null}}
{"v":1,"type":"record_cancel","request_id":"r1","session_id":"review-42","payload":{}}
{"v":1,"type":"shutdown","request_id":"s1","session_id":"review-42","payload":{}}
```

Beispiel Worker → Python:

```json
{"v":1,"type":"status","request_id":"c1","session_id":"review-42","payload":{"state":"model_ready"}}
{"v":1,"type":"status","request_id":"r1","session_id":"review-42","payload":{"state":"recording"}}
{"v":1,"type":"transcript","request_id":"r1","session_id":"review-42","payload":{"text":"la casa","language":"it","duration_ms":1450}}
{"v":1,"type":"error","request_id":"r1","session_id":"review-42","payload":{"code":"microphone_unavailable","message":"..."}}
```

Die Konfiguration kann erst dann als erfolgreich gelten, wenn `model_ready` zurückkommt. Es gibt auch `record_stop`, `cancelled` und `heartbeat` nur bei Bedarf; alle Nachrichtentypen werden zunächst als enum/Schema definiert. Vertrag in `tests/test_protocol.py` testen.

## Event- und Race-Handling

- Neue Karte → neue `session_id` (kombiniert Profil/Review-Generation/Karten-ID oder UUID), alle in-flight-Ergebnisse der alten Session verwerfen; aktive Aufnahme abbrechen.
- Nächste `record_start` während `recording` → mit definierter `busy`-Antwort ablehnen.
- Worker-Timeout → sicher abbrechen und UI-Status `error`; Nutzer kann normalen Review nutzen.
- Worker-Exit → Controller meldet `unavailable` und ermöglicht kontrollierten Neustart.
- Anki-Profilwechsel/Anki-Ende → orderly shutdown, dann nur als Fallback Unterprozess terminieren.
- Keine `waitForFinished()` oder blockierende `subprocess.run()` auf dem Anki-GUI-Thread.

## Ressourcen / Pfade

- Ausführbares Worker-Skript relativ zu `Path(__file__).resolve().parent / "worker" / "main.py"` bestimmen.
- Interpreter-Pfad aus Add-on-Konfiguration; für Entwickler voreingestellt auf `.venv/bin/python` **aus dem Repository**, aber Distribution benötigt eine dokumentierte externe Runtime-Installation.
- Keine feste Annahme, dass der aktuelle Anki-Prozess `python3` heißt, dass `cwd` Repository ist oder dass ein Symlink den echten Elternpfad erhält.
- Modellcache außerhalb des Add-on-Paketordners; Einstellungen in Anki-Konfiguration.
