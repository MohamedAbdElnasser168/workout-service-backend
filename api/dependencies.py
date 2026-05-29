"""
FastAPI Dependency Injection.

Provides shared dependencies (e.g., AI settings, rate limiters)
that can be injected into route handlers via FastAPI's Depends().
"""

from ai_model.config import AIModelSettings, get_ai_settings


async def get_ai_config() -> AIModelSettings:
    """Dependency that provides the AI configuration singleton."""
    return get_ai_settings()
