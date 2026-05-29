"""
API Request Schemas.

Pydantic models that validate incoming request data from the frontend.
These are separate from the AI internal schemas to maintain a clean
boundary between the API layer and the AI layer.
"""

from pydantic import BaseModel, Field
from enum import Enum


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class FitnessGoal(str, Enum):
    LOSE_WEIGHT = "Lose Weight"
    BUILD_MUSCLE = "Build Muscle"
    MAINTAIN = "Maintain"


class ActivityLevel(str, Enum):
    SEDENTARY = "Sedentary"
    LIGHTLY_ACTIVE = "Lightly Active"
    MODERATELY_ACTIVE = "Moderately Active"
    VERY_ACTIVE = "Very Active"
    EXTRA_ACTIVE = "Extra Active"


class WorkoutPlanRequest(BaseModel):
    """
    Validates the user profile data sent from the frontend form.

    Example payload:
    {
        "age": 25,
        "gender": "Male",
        "height_cm": 175.0,
        "weight_kg": 70.0,
        "goal": "Build Muscle",
        "activity_level": "Moderately Active"
    }
    """

    age: int = Field(
        ...,
        ge=13,
        le=100,
        description="User's age in years",
        examples=[25],
    )
    gender: Gender = Field(
        ...,
        description="User's gender",
        examples=["Male"],
    )
    height_cm: float = Field(
        ...,
        ge=100.0,
        le=250.0,
        description="User's height in centimeters",
        examples=[175.0],
    )
    weight_kg: float = Field(
        ...,
        ge=30.0,
        le=300.0,
        description="User's weight in kilograms",
        examples=[70.0],
    )
    goal: FitnessGoal = Field(
        ...,
        description="Primary fitness goal",
        examples=["Build Muscle"],
    )
    activity_level: ActivityLevel = Field(
        ...,
        description="Current activity level",
        examples=["Moderately Active"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": 25,
                    "gender": "Male",
                    "height_cm": 175.0,
                    "weight_kg": 70.0,
                    "goal": "Build Muscle",
                    "activity_level": "Moderately Active",
                }
            ]
        }
    }
