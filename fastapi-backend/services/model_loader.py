from typing import Optional

from faster_whisper import WhisperModel


class ModelLoader:
    _whisper_model: Optional[WhisperModel] = None

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8") -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

    def get_whisper(self) -> WhisperModel:
        if ModelLoader._whisper_model is None:
            ModelLoader._whisper_model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
        return ModelLoader._whisper_model
