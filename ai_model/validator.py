"""
AI Output Validator.

Parses and validates the raw JSON string returned by the LLM against the
WorkoutPlan Pydantic model. Handles common LLM output issues like markdown
fences wrapping the JSON.
"""

import json
import re
import logging

from .schemas import WorkoutPlan

logger = logging.getLogger(__name__)


class AIOutputValidationError(Exception):
    """Raised when the AI output cannot be parsed or validated."""

    def __init__(self, message: str, raw_output: str | None = None):
        self.raw_output = raw_output
        super().__init__(message)


def _extract_json(raw: str) -> str:
    """
    Extracts JSON from raw LLM output, stripping markdown code fences
    or any surrounding text.
    """
    # Try to find JSON inside ```json ... ``` blocks
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Try to find raw JSON object
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return match.group(0).strip()

    return raw.strip()


def validate_workout_output(raw_output: str) -> WorkoutPlan:
    """
    Validates and parses raw LLM output into a WorkoutPlan model.

    Args:
        raw_output: The raw string response from the LLM.

    Returns:
        A validated WorkoutPlan instance.

    Raises:
        AIOutputValidationError: If the output is not valid JSON or
                                 doesn't conform to the WorkoutPlan schema.
    """
    cleaned = _extract_json(raw_output)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse AI output as JSON: %s", e)
        raise AIOutputValidationError(
            f"AI output is not valid JSON: {e}",
            raw_output=raw_output,
        ) from e

    try:
        plan = WorkoutPlan.model_validate(data)
    except Exception as e:
        logger.error("AI output does not match WorkoutPlan schema: %s", e)
        raise AIOutputValidationError(
            f"AI output does not conform to expected schema: {e}",
            raw_output=raw_output,
        ) from e

    logger.info("Successfully validated workout plan: %s", plan.plan_name)
    return plan
