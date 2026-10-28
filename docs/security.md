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
