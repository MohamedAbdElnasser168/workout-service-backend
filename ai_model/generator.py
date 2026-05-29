"""
Workout Plan Generator.

Core orchestration module that:
1. Builds the prompt from user data.
2. Sends it to the configured AI provider (OpenAI, Anthropic, or local).
3. Validates the response.
4. Returns a structured WorkoutPlan.

Supports retry logic for transient failures and malformed outputs.
"""

import logging
import json
import asyncio
import httpx

from .config import get_ai_settings, AIProvider
from .prompts import build_workout_prompt
from .schemas import WorkoutPlan
from .validator import validate_workout_output, AIOutputValidationError
from .template_generator import generate_template_workout

logger = logging.getLogger(__name__)

BASE_RETRY_DELAY = 5  # seconds — doubles each attempt (5s, 10s, 20s, 40s)


# ---------------------------------------------------------------------------
# Provider-specific generation functions
# ---------------------------------------------------------------------------

async def _generate_openai(system: str, user: str) -> str:
    """Calls the OpenAI Chat Completions API."""
    settings = get_ai_settings()

    async with httpx.AsyncClient(timeout=settings.generation_timeout) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openai_model,
                "temperature": settings.openai_temperature,
                "max_tokens": settings.openai_max_tokens,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def _generate_anthropic(system: str, user: str) -> str:
    """Calls the Anthropic Messages API."""
    settings = get_ai_settings()

    async with httpx.AsyncClient(timeout=settings.generation_timeout) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.anthropic_model,
                "max_tokens": settings.anthropic_max_tokens,
                "temperature": settings.anthropic_temperature,
                "system": system,
                "messages": [
                    {"role": "user", "content": user},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]


async def _generate_gemini(system: str, user: str) -> str:
    """Calls the Google Gemini API (free tier: 15 RPM)."""
    settings = get_ai_settings()
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    )

    async with httpx.AsyncClient(timeout=settings.generation_timeout) as client:
        response = await client.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {
                    "parts": [{"text": system}]
                },
                "contents": [
                    {"role": "user", "parts": [{"text": user}]}
                ],
                "generationConfig": {
                    "temperature": settings.gemini_temperature,
                    "maxOutputTokens": settings.gemini_max_tokens,
                    "responseMimeType": "application/json",
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def _generate_local(system: str, user: str) -> str:
    """Calls a local model endpoint (e.g., Ollama)."""
    settings = get_ai_settings()

    async with httpx.AsyncClient(timeout=settings.generation_timeout) as client:
        response = await client.post(
            settings.local_model_url,
            json={
                "model": settings.local_model_name,
                "prompt": f"{system}\n\n{user}",
                "stream": False,
                "format": "json",
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]


# ---------------------------------------------------------------------------
# Provider dispatch map
# ---------------------------------------------------------------------------

_PROVIDER_MAP = {
    AIProvider.OPENAI: _generate_openai,
    AIProvider.ANTHROPIC: _generate_anthropic,
    AIProvider.GEMINI: _generate_gemini,
    AIProvider.LOCAL: _generate_local,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

AI_TIMEOUT_SECONDS = 10  # Hard timeout — fallback to templates after this


async def _try_ai_generation(
    generate_fn,
    prompts: dict[str, str],
    max_retries: int,
    provider_name: str,
) -> WorkoutPlan:
    """Attempts AI generation with retries. Meant to be wrapped in a timeout."""
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                "Generation attempt %d/%d using provider=%s",
                attempt,
                max_retries,
                provider_name,
            )
            raw_output = await generate_fn(prompts["system"], prompts["user"])
            plan = validate_workout_output(raw_output)
            return plan

        except AIOutputValidationError as e:
            logger.warning("Attempt %d failed validation: %s", attempt, e)
            last_error = e
        except httpx.HTTPStatusError as e:
            logger.error("API call failed on attempt %d: %s", attempt, e)
            last_error = e
        except Exception as e:
            logger.error("Unexpected error on attempt %d: %s", attempt, e)
            last_error = e

    raise AIOutputValidationError(
        f"All {max_retries} AI attempts failed. Last error: {last_error}"
    )


async def generate_workout_plan(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    goal: str,
    activity_level: str,
) -> WorkoutPlan:
    """
    Generates a personalized workout plan.

    Strategy:
        1. Try AI generation with a hard timeout of 10 seconds.
        2. If AI succeeds within 10s → return AI-generated plan.
        3. If AI fails or times out → instantly fallback to template-based plan.

    This guarantees the user ALWAYS gets a response within ~10 seconds.
    """
    settings = get_ai_settings()
    prompts = build_workout_prompt(
        age=age,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        goal=goal,
        activity_level=activity_level,
    )

    generate_fn = _PROVIDER_MAP[settings.ai_provider]
    fallback_args = dict(age=age, gender=gender, height_cm=height_cm,
                         weight_kg=weight_kg, goal=goal, activity_level=activity_level)

    try:
        plan = await asyncio.wait_for(
            _try_ai_generation(
                generate_fn=generate_fn,
                prompts=prompts,
                max_retries=settings.max_retries,
                provider_name=settings.ai_provider.value,
            ),
            timeout=AI_TIMEOUT_SECONDS,
        )
        logger.info("AI generation succeeded within %ds timeout.", AI_TIMEOUT_SECONDS)
        return plan

    except asyncio.TimeoutError:
        logger.warning(
            "AI generation timed out after %d seconds. Using template fallback.",
            AI_TIMEOUT_SECONDS,
        )
    except Exception as e:
        logger.warning("AI generation failed: %s. Using template fallback.", e)

    return generate_template_workout(**fallback_args)
