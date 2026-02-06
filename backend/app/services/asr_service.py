from __future__ import annotations

from typing import Optional

from app.utils.settings import settings

_openai_whisper_model = None
_faster_whisper_model = None


def _transcribe_with_openai_whisper(file_path: str, language: str | None) -> str:
    global _openai_whisper_model
    import whisper  # type: ignore

    if _openai_whisper_model is None:
        _openai_whisper_model = whisper.load_model(settings.whisper_model)
    result = _openai_whisper_model.transcribe(file_path, language=language)
    return result.get("text", "").strip()


def _transcribe_with_faster_whisper(file_path: str, language: str | None) -> str:
    global _faster_whisper_model
    from faster_whisper import WhisperModel  # type: ignore

    if _faster_whisper_model is None:
        _faster_whisper_model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
    segments, _info = _faster_whisper_model.transcribe(file_path, language=language)
    return "".join(seg.text for seg in segments).strip()


def transcribe_audio(file_path: str, language: str | None = None) -> str:
    backend = settings.asr_backend or "auto"
    last_error: Optional[Exception] = None

    if backend in ("auto", "openai-whisper"):
        try:
            return _transcribe_with_openai_whisper(file_path, language)
        except Exception as exc:  # pragma: no cover - env-specific
            last_error = exc
            if backend == "openai-whisper":
                raise

    if backend in ("auto", "faster-whisper"):
        try:
            return _transcribe_with_faster_whisper(file_path, language)
        except Exception as exc:  # pragma: no cover - env-specific
            last_error = exc
            if backend == "faster-whisper":
                raise

    raise RuntimeError(
        "ASR backend unavailable. "
        "Set ASR_BACKEND=openai-whisper or faster-whisper and ensure dependencies are installed. "
        f"Last error: {last_error}"
    )
