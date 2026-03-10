"""Centralized settings (env-driven)."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Meeting Minutes STT"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-it-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:postgres@localhost:5432/meeting_minutes_db"
    
    # Whisper
    # Use 'ggml-small.bin' for better accuracy, 'ggml-base.bin' for speed
    WHISPER_MODEL_PATH: str = "./models/ggml-small.bin"
    # Assuming using a binary wrapper or python binding, path to binary if needed
    WHISPER_BINARY_PATH: str = "./whisper/main.exe"
    FFMPEG_BINARY_PATH: str = "./ffmpeg/bin/ffmpeg.exe"

    # Storage
    UPLOAD_DIR: str = "uploads"
    AUDIO_DIR: str = "uploads/audio"
    PDF_DIR: str = "uploads/pdf"

    # AI Integration
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

