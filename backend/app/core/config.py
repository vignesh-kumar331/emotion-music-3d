from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "Emotion Music Companion"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./emotion_music.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "emotion-music-secret-key-change-32chars!!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: list[str] = ["http://localhost:5173","http://localhost:5174","http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
