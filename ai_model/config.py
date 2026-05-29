"""
AI Model Configuration.

Centralizes all configuration for the AI provider (OpenAI, Anthropic, local model, etc.).
Loads sensitive values from environment variables via pydantic-settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum


class AIProvider(str, Enum):
    """Supported AI providers for workout plan generation."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"  # Google Gemini (generous free tier)
    LOCAL = "local"  # For self-hosted models (e.g., Ollama, vLLM)


class AIModelSettings(BaseSettings):
    """
    Configuration for the AI model service.
    Values are loaded from environment variables or a .env file.
    """

    # --- Provider Selection ---
    ai_provider: AIProvider = AIProvider.OPENAI

    # --- OpenAI ---
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 4096

    # --- Anthropic ---
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_temperature: float = 0.7
    anthropic_max_tokens: int = 4096

    # --- Google Gemini (free tier: 15 RPM) ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 4096

    # --- Local Model (e.g., Ollama) ---
    local_model_url: str = "http://localhost:11434/api/generate"
    local_model_name: str = "llama3"

    # --- General ---
    generation_timeout: int = 60  # seconds
    max_retries: int = 3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_ai_settings() -> AIModelSettings:
    """Returns a cached singleton of the AI settings."""
    return AIModelSettings()
