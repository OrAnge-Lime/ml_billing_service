import whisper # from openai-whisper
import torch
import logging
import os
from typing import Any, Dict, Optional

from ml_models.base import AbstractMLModel # Corrected import
from config import asr_settings

logger = logging.getLogger(__name__)

class WhisperASR(AbstractMLModel):
    """Concrete implementation for OpenAI Whisper models."""

    def __init__(self, config: Dict[str, Any]):
        self.model_name = config.get("model_name", "base")
        self.device = config.get("device", asr_settings.DEFAULT_DEVICE)
        self.model_download_root = asr_settings.MODEL_CACHE_DIRECTORY
        try:
            os.makedirs(self.model_download_root, exist_ok=True)
        except:
           logger.info(f"Failed to create '{self.model_download_root}'.") 

        logger.info(f"Initializing Whisper model: {self.model_name} on device: {self.device}")
        logger.info(f"Models will be downloaded/cached at: {self.model_download_root}")

        try:
            self.model = whisper.load_model(
                self.model_name,
                device=self.device,
                download_root=self.model_download_root
            )
            logger.info(f"Whisper model '{self.model_name}' loaded successfully onto '{self.device}'.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model '{self.model_name}': {e}")
            raise RuntimeError(f"Whisper model loading failed: {e}") from e

    async def predict(self, audio_file_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Transcribes audio using the loaded Whisper model.
        kwargs can include 'language' (str) and 'task' (str: 'transcribe' or 'translate').
        """
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found at: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        language = kwargs.get("language")
        task = kwargs.get("task", "transcribe") # Default to transcribe

        logger.info(f"Transcribing audio: {audio_file_path} with model: {self.model_name}, lang: {language}, task: {task}")

        try:
            transcribe_options = {"fp16": torch.cuda.is_available() and self.device == "cuda"}
            if language:
                transcribe_options["language"] = language
            result = self.model.transcribe(audio_file_path, task=task, **transcribe_options)


            logger.info(f"Transcription successful for: {audio_file_path}")
            return {
                "text": result.get("text", ""),
                "language_detected": result.get("language", None),
                "segments": result.get("segments", [])
            }

        except Exception as e:
            logger.error(f"Error during Whisper transcription for {audio_file_path}: {e}")
            raise RuntimeError(f"Transcription failed: {e}") from e
        finally:
             if self.device == "cuda" and torch.cuda.is_available():
                 torch.cuda.empty_cache()