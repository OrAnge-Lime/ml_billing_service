import os
from pydantic_settings import BaseSettings
import torch 

class ASRSettings(BaseSettings):
    """Settings for the ASR service."""
    MODEL_CACHE_DIRECTORY: str = os.getenv("MODEL_CACHE_DIRECTORY", "./models_cache")
    # MODEL_CACHE_DIRECTORY: str = "./models_cache"

    # Define specific Whisper model configurations
    MODEL_CONFIGS: dict = {
        "whisper-tiny": {
            "type": "whisper",
            "model_name": "tiny", 
        },
        "whisper-base": {
            "type": "whisper",
            "model_name": "base",
        },
        "whisper-small": {
            "type": "whisper",
            "model_name": "small",
        },
        "whisper-medium": {
            "type": "whisper",
            "model_name": "medium",
        },
        "whisper-large": { 
            "type": "whisper",
            "model_name": "large-v3", # large, large-v2, large-v3
        }
    }
    DEFAULT_DEVICE: str = os.getenv("DEFAULT_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")

    class Config:
        env_file = ".env.asr"
        env_file_encoding = 'utf-8'
        extra = 'ignore'

asr_settings = ASRSettings()