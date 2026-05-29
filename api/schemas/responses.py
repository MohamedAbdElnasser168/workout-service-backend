"""
API Response Schemas.

Wraps the AI-generated workout plan in a standardized API response envelope.
"""

from pydantic import BaseModel
from ai_model.schemas import WorkoutPlan


class WorkoutPlanResponse(BaseModel):
    """Successful response containing the generated workout plan."""
    success: bool = True
    message: str = "Workout plan generated successfully."
    data: WorkoutPlan


class ErrorResponse(BaseModel):
    """Standardized error response."""
    success: bool = False
    message: str
    detail: str | None = None
