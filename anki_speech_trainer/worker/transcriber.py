"""Long-lived local Faster-Whisper model wrapper."""

from __future__ import annotations

import time
from dataclasses import dataclass

try:  # Supports direct execution of main.py by QProcess.
    from audio import AudioCapture
except ImportError:  # pragma: no cover - exercised when imported as a package
    from .audio import AudioCapture


class TranscriptionError(RuntimeError):
    """A model setup or inference error safe to expose as a generic status."""


@dataclass(frozen=True)
class Transcript:
    text: str
    duration_ms: int


class LocalTranscriber:
    """Load exactly one multilingual model and reuse it between card requests."""

    def __init__(self) -> None:
        self._model: object | None = None
        self._configuration: tuple[str, str, str] | None = None

    def configure(self, *, model: str, device: str, compute_type: str) -> int:
        configuration = (model, device, compute_type)
        if self._model is not None and self._configuration == configuration:
            return 0
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover - runtime setup failure
            raise TranscriptionError("model_unavailable") from exc
        started_at = time.perf_counter()
        try:
            self._model = WhisperModel(model, device=device, compute_type=compute_type)
        except Exception as exc:
            self._model = None
            raise TranscriptionError("model_unavailable") from exc
        self._configuration = configuration
        return round((time.perf_counter() - started_at) * 1_000)

    def transcribe(self, audio: AudioCapture, *, language: str) -> Transcript:
        if self._model is None:
            raise TranscriptionError("model_not_ready")
        try:
            import numpy

            samples = numpy.frombuffer(audio.pcm, dtype=numpy.int16).astype(numpy.float32) / 32768.0
            started_at = time.perf_counter()
            segments, _info = self._model.transcribe(
                samples,
                language=language,
                condition_on_previous_text=False,
                beam_size=1,
                vad_filter=False,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            return Transcript(
                text=text, duration_ms=round((time.perf_counter() - started_at) * 1_000)
            )
        except Exception as exc:
            raise TranscriptionError("transcription_failed") from exc
