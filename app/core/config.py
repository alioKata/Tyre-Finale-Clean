# app/core/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="env.config", env_file_encoding="utf-8")

    APP_NAME: str = "AliProject API"
    HOST: str = "0.0.0.0"  # Changed from 127.0.0.1 to 0.0.0.0 for deployment
    PORT: int = int(os.environ.get("PORT", 8000))

    # JWT settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-jwt-secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Switch to SQLite for testing - this should work without authentication issues
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    # Email settings
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-smtp-user"
    SMTP_PASS: str = "password"
    EMAIL_FROM: str = "no-reply@yourdomain.com"

    FRONTEND_URL: str = "http://localhost:8000/verification"

    MODEL_PATH: str = "models/hybrid_model.h5"
    CLASS_INDICES_PATH: str = "models/class_indices.json"

settings = Settings()
