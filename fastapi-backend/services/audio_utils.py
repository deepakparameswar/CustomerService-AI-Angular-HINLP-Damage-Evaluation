import os
from typing import Optional


def resolve_audio_path(audio_url: str) -> str:
    if audio_url.startswith("http"):
        if "/audio_uploads/" in audio_url:
            audio_name = audio_url.split("/audio_uploads/")[-1]
            return os.path.join("audio_uploads", audio_name)
        return audio_url
    return audio_url


def _fallback_audio_path(original_path: str) -> str:
    if os.path.exists(original_path):
        return original_path

    audio_dir = "audio_uploads"
    if not os.path.isdir(audio_dir):
        return original_path

    target_name = os.path.basename(original_path).lower()
    candidates = [
        f for f in os.listdir(audio_dir)
        if os.path.isfile(os.path.join(audio_dir, f))
    ]

    for filename in candidates:
        if filename.lower() == target_name:
            return os.path.join(audio_dir, filename)

    if len(candidates) == 1:
        return os.path.join(audio_dir, candidates[0])

    return original_path


def get_audio_path(audio_url: str) -> str:
    return _fallback_audio_path(resolve_audio_path(audio_url))


def validate_audio(audio_path_or_url: str) -> bool:
    if not audio_path_or_url:
        return False

    resolved_path = get_audio_path(audio_path_or_url)
    return os.path.exists(resolved_path)
