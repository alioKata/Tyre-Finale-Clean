# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="env.config")

    APP_NAME: str = "AliProject API"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # JWT settings
    SECRET_KEY: str = "your-jwt-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Switch to SQLite for testing - this should work without authentication issues
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Email settings
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-smtp-user"
    SMTP_PASS: str = "password"
    EMAIL_FROM: str = "no-reply@yourdomain.com"

    FRONTEND_URL: str = "http://localhost:8000/verification"

    MODEL_PATH: str = "models/custom_model.h5"
    CLASS_INDICES_PATH: str = "models/class_indices.json"

settings = Settings()
