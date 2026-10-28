# Privacy, security, and release

## Privacy

Microphone capture starts only after a visible learner click. Audio PCM and the
transcript remain in memory for the current attempt; they are not written to
Anki notes, the collection, logs, analytics, or cloud services. The worker runs
no HTTP server and makes no network request while reviewing a cached model.

## Trusted dependencies and model provisioning

Runtime packages are exact versions in `requirements-worker.txt`; development
tools, including `pip-audit`, are in `requirements-dev.txt`. Before a public
release, create a clean virtual environment, install the two requirements
files, and run:

```bash
.venv/bin/python -m pip check
.venv/bin/python -m pip_audit -r requirements-worker.txt
```

An advisory audit is evidence about known package vulnerabilities, not proof
that a package is safe. Resolve or explicitly document any reported finding
before release.

Use only the configured, known Faster-Whisper model identifier (the default is
`base`) or a local model directory provisioned by the maintainer. Record the
model identifier, upstream repository revision, and SHA-256 of each downloaded
snapshot in the release notes or a private release record. Do not distribute
model weights inside the add-on archive. First provisioning may require network
access; subsequent cached use can be offline. Replace an unexpected or
unverifiable model cache instead of trusting it.

## Archive and publication checklist

1. Verify no local paths, personal configuration, credentials, model caches,
   `.venv`, or `meta.json` are tracked or archived.
2. Run `just check`, then the dependency commands above.
3. Run `just build-addon` and confirm the archive has root
   `__init__.py`, `manifest.json`, `config.json`, runtime files, and the
   full `LICENSE` only.
4. Install the archive into a backed-up disposable Anki profile and perform a
   microphone, mapping, cancellation, and offline-cache smoke test.
5. Publish corresponding source with its complete AGPL-3.0-or-later text and
   link the public repository and issue tracker as AnkiWeb's Support Page.

The generated archive deliberately excludes worker dependencies and model
weights: users install the worker in their own environment, which keeps Anki's
bundled Python isolated.
