"""
Workout Plan Route.

POST /api/v1/workout-plan
Accepts user profile data, calls the AI generator, returns a structured plan.
"""

import logging

from fastapi import APIRouter, HTTPException
from api.schemas.requests import WorkoutPlanRequest
from api.schemas.responses import WorkoutPlanResponse, ErrorResponse
from ai_model.generator import generate_workout_plan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Workout Plan"])


@router.post(
    "/workout-plan",
    response_model=WorkoutPlanResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Generate a Personalized Workout Plan",
    description="Accepts user profile data and returns a personalized 7-day workout plan.",
)
async def create_workout_plan(request: WorkoutPlanRequest) -> WorkoutPlanResponse:
    """
    Main endpoint that bridges the API layer to the template generator.

    Flow:
        1. Pydantic validates the incoming request body automatically.
        2. The validated data is passed to the generator.
        3. The generator personalizes the plan based on user metrics.
        4. The WorkoutPlan is wrapped in a response envelope.
    """
    try:
        plan = await generate_workout_plan(
            age=request.age,
            gender=request.gender.value,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            goal=request.goal.value,
            activity_level=request.activity_level.value,
        )

        return WorkoutPlanResponse(
            success=True,
            message="Workout plan generated successfully.",
            data=plan,
        )

    except Exception as e:
        logger.exception("Unexpected error generating workout plan: %s", e)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "An internal server error occurred.",
            },
        )
