"""
Configuration settings for Phani AI Platform.
Handles environment variables, API credentials, database URIs, and default system settings.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# Helper to load key from os.environ or Streamlit secrets
def get_secret(key_name: str, default: str = "") -> str:
    val = os.environ.get(key_name, "")
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key_name in st.secrets:
            return str(st.secrets[key_name])
    except Exception:
        pass
    return default


class Settings:
    # App Info
    APP_NAME: str = "Phani AI"
    APP_DESCRIPTION: str = (
        "Phani AI is a multi-purpose AI assistant that combines conversational AI, "
        "real-time information services, multimedia generation, and intelligent query routing in a single platform."
    )
    APP_VERSION: str = "2.0.0"

    # API Keys
    GEMINI_API_KEY: str = get_secret("GEMINI_API_KEY")
    WEATHER_API_KEY: str = get_secret("WEATHER_API_KEY")
    NEWS_API_KEY: str = get_secret("NEWS_API_KEY")
    SPORTS_API_KEY: str = get_secret("SPORTS_API_KEY")
    STOCK_API_KEY: str = get_secret("STOCK_API_KEY")
    CRYPTO_API_KEY: str = get_secret("CRYPTO_API_KEY")
    IMAGE_API_KEY: str = get_secret("IMAGE_API_KEY")
    VIDEO_API_KEY: str = get_secret("VIDEO_API_KEY")

    # Database Settings
    DATABASE_URL: str = get_secret("DATABASE_URL", f"sqlite:///{BASE_DIR / 'phani_ai.db'}")

    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 900  # 15 minutes default TTL for real-time services

    # Rate Limiting
    MAX_QUERIES_PER_MINUTE: int = 60

    # Service Timeouts (seconds)
    API_TIMEOUT: float = 8.0


settings = Settings()
