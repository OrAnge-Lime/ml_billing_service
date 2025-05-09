import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/ml_service_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # ASR Service settings
    ASR_SERVICE_URL: str = os.getenv("ASR_SERVICE_URL", "http://asr_service:8011") # Updated port, service name
    ASR_REQUEST_TIMEOUT_SEC: int = int(os.getenv("ASR_REQUEST_TIMEOUT_SEC", 300)) # Increased timeout for ASR

    class Config:
        # If not using load_dotenv(), pydantic can load from .env directly
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields from .env

settings = Settings()
logger.info(f"Main API Loaded Settings: ASR_SERVICE_URL={settings.ASR_SERVICE_URL}")