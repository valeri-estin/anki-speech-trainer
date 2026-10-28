# 16 — Add-on distribution

## Release archive

Run `just build-addon` from the repository root. It writes
`dist/anki-speech-trainer-<version>.ankiaddon` and validates that the archive
has `__init__.py`, `config.json`, `manifest.json`, and the worker entry point at
the required archive paths.

The archive includes only `anki_speech_trainer/` runtime files. It excludes
virtual environments, model caches, bytecode, test files, and Anki-generated
`meta.json`. The latter may contain a machine-specific worker interpreter path
and must never be distributed.

`manifest.json` owns the stable package identifier used for upgrades. Keep
`package` equal to `anki_speech_trainer`; update only `human_version` for each
release. The declared Anki minimum is 26.09 because that is the runtime version
against which this add-on has been verified.

## User installation and use

1. Install the external worker dependencies from `requirements-worker.txt` in a
   personal Python virtual environment; never install them into Anki's bundled
   Python environment.
2. Build or download the `.ankiaddon` archive, then in Anki Desktop select
   **Tools → Add-ons → Install from file…** and restart Anki.
3. Open the add-on's configuration and set `worker_python` to the absolute path
   of that virtual environment's Python executable.
4. Add a `notetype_mappings` entry for a note type and answer field that exist
   in the active collection. For `Italian Practice`, scope the mapping to the
   `Speaking` template and use `Target` as the answer field.
5. Review a mapped card, click **Sprechen**, and speak the expected answer. The
   displayed transcript is guidance only; use Anki's native **Again**, **Hard**,
   **Good**, and **Easy** controls to schedule the card.

Install and first-run test the archive in a backed-up disposable collection.
Do not install it over an active development symlink using the same package
identifier; remove or relocate that link only after closing Anki and confirming
its target.
