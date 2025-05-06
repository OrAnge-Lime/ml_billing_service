import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/ml_service_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    MODEL_DIRECTORY: str = os.getenv("MODEL_DIRECTORY", "./models")

    class Config:
        # If not using load_dotenv(), pydantic can load from .env directly
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields from .env

settings = Settings()

# Optional: Print loaded settings for verification during startup
# print(f"Loaded settings: DATABASE_URL={settings.DATABASE_URL}, SECRET_KEY={'*' * 5}, ALGORITHM={settings.ALGORITHM}")