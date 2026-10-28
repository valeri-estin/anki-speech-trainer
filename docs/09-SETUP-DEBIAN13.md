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

## 2. Obtain the implemented repository

Clone or otherwise copy the full repository, which already includes the
implemented `anki_speech_trainer/` package, tests, scripts, and documentation:

```bash
git clone YOUR_REPOSITORY_URL ~/dev/anki-speech-trainer
cd ~/dev/anki-speech-trainer
```

## 3. Python-Umgebung nur für den Worker

```bash
cd ~/dev/anki-speech-trainer
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-worker.txt -r requirements-dev.txt
```

Die getesteten Versionen sind in `requirements-worker.txt` und `requirements-dev.txt` gepinnt.
Sie gehören ausschließlich in diese externe virtuelle Umgebung, niemals in Ankis eigene
Python-Umgebung.

## 4. Sound- und Modelltest

```bash
just spike --list-devices
just spike --record --device DEVICE_ID
```

Der zweite Befehl öffnet das Mikrofon erst durch den expliziten `--record`-Schalter, stoppt bei
Sprachpause und gibt gemessene Modell-/Transkriptionszeiten aus. Er kann einmalig das Modell
herunterladen; Internetverbindung und verfügbarer Speicher werden dafür gebraucht. Nach dem
ersten Download mit gecachtem Modell den Offline-Test aus Abschnitt 8 ausführen.

## 5. Development symlink installation

For iterative development, link the implemented package while Anki is closed:

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

For an installable archive instead, use `just build-addon` and follow
`docs/16-DISTRIBUTION.md`. Do not use both mechanisms with the same package
identifier at the same time.

## 6. Abschlussprüfung

- Anki ohne Worker startet normal.
- Normale (nicht gemappte) Karten zeigen keine Add-on-UI.
- Der Worker kann Audio aufnehmen und auf einer Testkarte transkribieren.
- Audio-/Modellfehler verursachen keinen Verlust des Lernfortschritts.
- Nach Netztrennung klappt ein vollständiger Durchlauf mit bereits gecachtem Modell.

Für die automatisierten Prüfungen im Repository:

```bash
just check
```
