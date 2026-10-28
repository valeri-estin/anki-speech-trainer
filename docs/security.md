# Security review

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
| A03 supply chain | Partially verified | Exact tested direct worker and development versions are in `requirements-*.txt`; advisory and integrity verification remains a release task. |
| A05 injection | Verified for spike inputs | No shell or HTML evaluation; numeric device IDs and argparse bounds are used. |
| A06 insecure design | Verified for scope | Recording requires an explicit flag, has start and maximum-duration bounds, and does not prime Whisper with an expected answer. |
| A09 logging | Verified for scope | Diagnostics use stderr and contain no PCM or transcript. The transcript is printed only as the explicit CLI result. |
| A10 exceptional conditions | Partially verified | Missing devices, invalid VAD timing, PortAudio errors, and model errors become bounded messages. Physical microphone recovery remains unverified because this environment exposes no audio device. |

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
| A10 exceptional conditions | Partially verified | Invalid configuration, unavailable worker, malformed worker responses, cancellation, worker exit, and stale sessions take a recoverable UI path. A real Qt/Anki test-profile run remains pending. |

The widget does not supply an authorization or trust boundary: all note text and worker output are
treated as untrusted display data. There are no remote endpoints, accounts, secrets, or
collection writes in this slice.

## Phase 2: worker audio and model lifecycle (2026-10-28)

| Area | Status | Evidence / control |
| --- | --- | --- |
| A03 supply chain | Partially verified | Tested package versions are pinned. Model cache provenance/integrity policy is delegated to Faster-Whisper/Hugging Face and must be documented for packaged distribution. |
| A06 resource exhaustion | Verified in code | Recording requires a click and has bounded initial-speech, silence, and maximum-duration limits; a concurrent `record_start` returns `busy`. |
| A09 privacy | Verified in code | PCM stays in process memory; no audio/text is written. Worker diagnostics never emit transcript text. |
| A10 recovery | Verified by unit and worker checks | Missing microphone, invalid configuration, busy recordings, cancellation, worker exit, and offline cached-model loading have recoverable protocol paths. Physical-device behavior remains unverified. |

The controller sends configuration only after Qt signals that worker stdin is running. It also
correlates configuration and recording response IDs; replies from cancelled attempts are ignored.
Transcripts are bounded to 4 KiB UTF-8 before a worker response is emitted, so a pathological
model response cannot bypass the JSONL message-size limit.

The controller also bounds model initialization and recording-to-result waits. Each timeout is
captured with its process, session, and request identity, so an old timer cannot terminate or
alter a newer worker session.

Expected worker termination during profile shutdown or timeout recovery is not presented as a
misleading worker-start error. Runtime diagnostics remain on worker stderr and are not persisted.
