# app/core/config.py

import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

# Set up logging
logger = logging.getLogger("app.config")

# Get PORT from environment with debug logging
env_port = os.environ.get("PORT")
logger.info(f"Environment PORT value: {env_port}")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="env.config", env_file_encoding="utf-8")

    APP_NAME: str = "AliProject API"
    HOST: str = "0.0.0.0"  # Changed from 127.0.0.1 to 0.0.0.0 for deployment
    
    # For PORT, we first check environment variable, then fallback to 8000
    # Important for Render.com deployment
    PORT: int = int(env_port) if env_port else 8000

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
logger.info(f"Initialized settings with PORT={settings.PORT}, HOST={settings.HOST}")
