"""
Workout Plan Generator.

Core orchestration module that generates plans using the rule-based local template generator.
"""

import logging
from .schemas import WorkoutPlan
from .template_generator import generate_template_workout

logger = logging.getLogger(__name__)


async def generate_workout_plan(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    goal: str,
    activity_level: str,
) -> WorkoutPlan:
    """
    Generates a personalized workout plan using local rule-based templates.
    """
    logger.info(
        "Generating template workout plan for goal=%s, activity_level=%s",
        goal,
        activity_level,
    )
    return generate_template_workout(
        age=age,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        goal=goal,
        activity_level=activity_level,
    )
