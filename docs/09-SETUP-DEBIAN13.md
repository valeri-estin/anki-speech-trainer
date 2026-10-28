# 09 — Debian-13-Setup und erster Entwicklungsstart

Diese Anleitung richtet sich an **eine bestehende Anki-Desktop-Installation**. Sie setzt **kein** vorgegebenes Anki-Binärpaket voraus.

## 0. Vorbereitung

1. Anki-Version prüfen (Anki → Hilfe → Über Anki); Versionsnummer ins Projekt-Log schreiben.
2. Anki **beenden** und ein **separates Testprofil** anlegen; produktive Profile nicht für Debugging verwenden.
3. Aktuelle Anki-Collection/Medien wie gewohnt sichern. Kein Add-on darf hierfür Daten ändern.
4. Arbeitsverzeichnis wählen, z. B. `~/dev/anki-speech-trainer`.

## 1. Pakete installieren

```bash
sudo apt update
sudo apt install -y git unzip python3 python3-venv python3-pip libportaudio2
```

Wenn Audioerkennung unter Debian scheitert, `sudo apt install -y alsa-utils` ergänzen und Eingabegeräte prüfen.

## 2. Starterpaket entpacken

Nach dem Download von `anki-speech-trainer-docs.zip` (Pfad anpassen):

```bash
mkdir -p ~/dev/anki-speech-trainer
cd ~/dev/anki-speech-trainer
unzip ~/Downloads/anki-speech-trainer-docs.zip
```

Die ZIP enthält bereits `AGENTS.md`, `README.md`, `CHANGELOG.md` und den vollständigen Ordner `docs/`; **noch kein programmiertes Add-on**.

## 3. Python-Umgebung nur für den Worker

```bash
cd ~/dev/anki-speech-trainer
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install faster-whisper sounddevice webrtcvad-wheels numpy pytest ruff
```

**Hinweis:** Die Bibliotheksversionen in diesem Bootstrap-Befehl sind bewusst noch nicht festgeschrieben. Der Agent muss nach erfolgreichem Technik-Spike die konkret getesteten Versionen in `requirements-worker.txt` und gegebenenfalls `requirements-dev.txt` festhalten. Nicht direkt in Ankis eigene Python-Umgebung installieren.

## 4. Sound- und Modelltest

```bash
.venv/bin/python -c 'import sounddevice as sd; print(sd.query_devices())'
.venv/bin/python -c 'from faster_whisper import WhisperModel; m = WhisperModel("base", device="cpu", compute_type="int8"); print("Modell geladen")'
```

Achtung: Der zweite Befehl kann einmalig **ein Modell herunterladen**. Internetverbindung und verfügbarer Speicher werden dafür gebraucht. Das ist ein Setup-Test, kein Mikrofon-/Transkriptionstest. Später wird Offline-Funktionalität getestet.

## 5. Git initialisieren

```bash
cd ~/dev/anki-speech-trainer
git init
git add .
git commit -m "docs: initialize Anki Speech Trainer specification"
```

Falls Git Nutzername/E-Mail noch nicht eingerichtet sind, diese zunächst lokal konfigurieren. Remote/`git push` **nur** bei von dir eingerichtetem Repository.

## 6. Agent mit dem Repository starten

Öffne das Repository in deinem Coding-Agenten (Arbeitsverzeichnis `~/dev/anki-speech-trainer`) und gib den in `docs/11-AGENT-PLAN.md` enthaltenen Startprompt ein. Erst Technik-Spike, dann Add-on.

## 7. Add-on beim tatsächlichen Implementieren verlinken

Erst wenn der Agent `anki_speech_trainer/__init__.py` und den Add-on-Code erstellt hat:

1. In Anki `Extras → Erweiterungen → Dateien anzeigen` öffnen und **den tatsächlichen** `addons21`-Pfad bestimmen.
2. Anki schließen.
3. Im Terminal aus dem Repository (nur wenn noch kein gleichnamiger Link/Ordner existiert):

```bash
cd ~/dev/anki-speech-trainer
mkdir -p ~/.local/share/Anki2/addons21
ln -s "$(realpath anki_speech_trainer)" ~/.local/share/Anki2/addons21/anki_speech_trainer
```

Der Beispielpfad gilt für Standard-Installationen unter Linux, nicht zwingend für Flatpak/Snap/portable Anki.

4. Anki wieder starten, **Testprofil** wählen, Add-on-Status prüfen. Eventuelle Fehler zuerst im Terminal/Anki-Add-on-Fehlerdialog prüfen.
5. In `config.json` bzw. Ankis Add-on-Konfiguration eine tatsächlich vorhandene Notiztyp-/Feldzuordnung und den **absoluten** Worker-Python-Pfad konfigurieren. Beispiel: `/home/DEIN-USER/dev/anki-speech-trainer/.venv/bin/python`.

## 8. Abschlussprüfung

- Anki ohne Worker startet normal.
- Normale (nicht gemappte) Karten zeigen keine Add-on-UI.
- Der Worker kann Audio aufnehmen und auf einer Testkarte transkribieren.
- Audio-/Modellfehler verursachen keinen Verlust des Lernfortschritts.
- Nach Netztrennung klappt ein vollständiger Durchlauf mit bereits gecachtem Modell.
