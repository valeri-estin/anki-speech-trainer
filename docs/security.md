# Security review

## Release dependency audit (2026-10-28)

The public-release dependency check installed the pinned development audit tool
and ran `just audit-deps` against `requirements-worker.txt`. `pip check`
reported no broken requirements and `pip-audit` reported no known
vulnerabilities at the time of the check. This covers known Python package
advisories only; it does not authenticate model data or prove a dependency is
otherwise safe. The publication checklist requires repeating it for every
release and recording trusted Faster-Whisper model provenance separately.

## Phase 0: isolated audio spike (2026-10-28)

### Trust boundaries

- The developer explicitly opts into microphone access with `--record`; captured PCM and
  returned text remain in RAM and are never written to disk.
- The local Hugging Face model cache is an external input to Faster-Whisper. The spike only
  accepts a model identifier or path supplied by the local developer; no network service,
  HTTP listener, Anki collection access, or shell command construction exists.
- PortAudio device IDs are parsed as non-negative integers. User-provided device names are
  intentionally not accepted, preventing ambiguous device selection and command injection.

### Focused OWASP review

| Area | Status | Evidence / control |
| --- | --- | --- |
| A03 supply chain | Partially verified | Exact tested direct worker and development versions are in `requirements-*.txt`; the public-release advisory check passed, while model-cache provenance remains a release responsibility. |
| A05 injection | Verified for spike inputs | No shell or HTML evaluation; numeric device IDs and argparse bounds are used. |
| A06 insecure design | Verified for scope | Recording requires an explicit flag, has start and maximum-duration bounds, and does not prime Whisper with an expected answer. |
| A09 logging | Verified for scope | Diagnostics use stderr and contain no PCM or transcript. The transcript is printed only as the explicit CLI result. |
| A10 exceptional conditions | Partially verified | Missing devices, invalid VAD timing, PortAudio errors, and model errors become bounded messages. The developer manually verified the normal physical-microphone path on 2026-10-28; recovery cases such as an unplugged device remain unverified. |

Other OWASP categories are not applicable to this standalone local spike: it has no accounts,
authorization, persistence, cryptography, remote endpoint, or external side effect.

## Follow-up boundary for the add-on

The JSONL worker transport must validate message size and schema, keep stdout protocol-only,
launch `QProcess` with an argument list rather than a shell, escape all transcript display as
text, and discard messages from stale review sessions. These controls are reviewed again in
Phase 1 and Phase 2.

## Phase 1: reviewer and IPC foundation (2026-10-28)

| Area | Status | Evidence / control |
| --- | --- | --- |
| A05 injection | Verified in code | JSONL has exact schema and 16 KiB bounds; `QProcess.start()` receives an executable plus argument list, never a shell; transcript rendering uses `textContent`. |
| A06 insecure design | Verified in code | Only configured fields are read, Cloze is excluded, session IDs reject stale answers, and no path reaches Anki scheduler or collection mutation APIs. |
| A08 integrity | Verified in code | Protocol version/type/request/session/payload fields are validated before dispatch; stdout remains protocol-only. |
| A10 exceptional conditions | Partially verified | Invalid configuration, unavailable worker, malformed worker responses, cancellation, worker exit, and stale sessions take a recoverable UI path. The developer manually exercised the mapped-card path in a real Anki test profile on 2026-10-28; unmapped-card and native-control edge cases remain pending. |

The widget does not supply an authorization or trust boundary: all note text and worker output are
treated as untrusted display data. There are no remote endpoints, accounts, secrets, or
collection writes in this slice.

## Phase 2: worker audio and model lifecycle (2026-10-28)

| Area | Status | Evidence / control |
| --- | --- | --- |
| A03 supply chain | Partially verified | Tested package versions are pinned and the release advisory check passed. Model-cache provenance/integrity remains a maintainer-controlled release task. |
| A06 resource exhaustion | Verified in code | Recording requires a click and has bounded initial-speech, silence, and maximum-duration limits; a concurrent `record_start` returns `busy`. |
| A09 privacy | Verified in code | PCM stays in process memory; no audio/text is written. Worker diagnostics never emit transcript text. |
| A10 recovery | Partially verified | Missing microphone, invalid configuration, busy recordings, cancellation, worker exit, and offline cached-model loading have recoverable protocol paths. The normal physical-device path was manually exercised on 2026-10-28; device-loss recovery remains unverified. |

The controller sends configuration only after Qt signals that worker stdin is running. It also
correlates configuration and recording response IDs; replies from cancelled attempts are ignored.
Transcripts are bounded to 4 KiB UTF-8 before a worker response is emitted, so a pathological
model response cannot bypass the JSONL message-size limit.

The controller also bounds model initialization and recording-to-result waits. Each timeout is
captured with its process, session, and request identity, so an old timer cannot terminate or
alter a newer worker session.

Expected worker termination during profile shutdown or timeout recovery is not presented as a
misleading worker-start error. Runtime diagnostics remain on worker stderr and are not persisted.

## Italian Practice package and template mapping (2026-10-28)

| Area | Status | Evidence / control |
| --- | --- | --- |
| A05 injection | Verified in code | The widget matches an exact `card.template()["name"]`; untrusted note and transcript values remain renderer text/Anki fields, never JavaScript bridge input. The CSV validator treats fields as data and reports only row numbers plus codes. |
| A06 insecure design | Verified in code | The package is built and verified only in temporary collections. The installed add-on does not create note types, cards, decks, media, or scheduler state. |
| A08 integrity | Partially verified | CSV IDs are required as the immutable first field, duplicate IDs are rejected before import, and template-required fields are checked. Anki import options remain a user decision; imports must use a separate profile first. |
| A10 exceptional conditions | Verified by automated checks | Invalid template/language mappings hide the widget. Missing enabled fields, duplicate IDs, absent listening audio tags, malformed CSV, and malformed packages fail with bounded non-content diagnostics. |

Anki package imports do not reliably remap static template deck-override IDs to a receiving
collection. The package intentionally contains no override IDs; the user assigns them once through
Anki after import. This avoids stale deck IDs and preserves the no-collection-mutation guarantee.

## Explicit language setup assistant (2026-10-28)

The normal review and worker paths remain collection-read-only. The new boundary is the visible,
user-clicked **Tools → Anki Speech Trainer → Sprach-Deck einrichten…** dialog. It has no network,
audio, subprocess, secret, or untrusted HTML input path.

| Area | Status | Evidence / control |
| --- | --- | --- |
| A05 injection | Verified in code | Display names reject control characters and `::`; language codes are bounded to lowercase two/three-letter values. Values are passed to Anki collection APIs, never a shell or HTML/JS. |
| A06 insecure design | Verified in code | No action occurs before a detailed preview plus confirmation. It creates only a clone and four new empty skill decks, never cards, notes, media, presets, scheduler state, or an existing object. The review path cannot invoke it. |
| A08 integrity | Verified in code | The source schema/template order is checked before cloning, exact target collisions are rejected, and the added mapping is scoped to the cloned `Speaking` template. |
| A10 exceptional conditions | Verified by unit and temporary-collection tests | Invalid inputs/source/collisions fail before writes. If model creation or config persistence fails after deck creation, best-effort cleanup targets only the IDs created by that invocation. A real Anki 26.09.3 temporary-collection verifier confirms source preservation and duplicate rejection. |

Manual desktop UI verification remains pending: confirm the preview/cancel path and successful menu
action in a disposable profile. This is a verification gap, not a known security finding.

The assistant now validates the neutral `Language Practice` source schema
(`TargetLanguageText` and `Translation`) before cloning. The older Italian
source schema remains legacy-only; the assistant never renames or migrates it.

## Interface localization (2026-10-28)

Focused review: `ui_language` is a local, user-controlled configuration value.
`language_from_config()` accepts only `en` and `de` and falls back to English.
The selected strings are serialized with JSON or passed to Qt as plain text;
review transcripts continue to use `textContent`. No configuration value reaches
a shell, collection query, or HTML interpolation without escaping.
