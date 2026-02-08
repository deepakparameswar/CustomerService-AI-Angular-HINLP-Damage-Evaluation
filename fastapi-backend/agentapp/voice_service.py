from typing import Optional, Tuple, Dict, Any

from services.audio_utils import validate_audio, get_audio_path
from services.model_loader import ModelLoader


def speech_to_text(audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
    """Transcribes audio file to text."""
    if not validate_audio(audio_path):
        return {"error": "Invalid audio path"}

    resolved_path = get_audio_path(audio_path)
    loader = ModelLoader()
    model = loader.get_whisper()

    if not model:
        return {"error": "Whisper model not initialized"}

    try:
        segments, info = model.transcribe(
            resolved_path,
            beam_size=5,
            language=language
        )

        text_segments = []
        for segment in segments:
            text_segments.append(segment.text)

        full_text = " ".join(text_segments).strip()

        result: Dict[str, Any] = {
            "text": full_text,
            "language": info.language
        }

        if info.language != "en":
            try:
                trans_segments, _ = model.transcribe(
                    resolved_path,
                    task="translate",
                    beam_size=5
                )
                trans_text = " ".join([s.text for s in trans_segments]).strip()
                result["translation"] = trans_text
            except Exception as e:
                result["translation_error"] = str(e)

        return result
    except Exception as e:
        return {"error": f"Transcription failed: {str(e)}"}


def transcribe_audio(audio_url: str, language: Optional[str] = None) -> Tuple[str, str]:
    result = speech_to_text(audio_url, language=language)
    if result.get("error"):
        raise ValueError(result["error"])

    text = result.get("text", "")
    detected_language = result.get("language") or (language or "unknown")
    return text, detected_language


def translate_audio(audio_url: str) -> str:
    result = speech_to_text(audio_url)
    if result.get("error"):
        raise ValueError(result["error"])

    if result.get("translation"):
        return result["translation"]

    return result.get("text", "")