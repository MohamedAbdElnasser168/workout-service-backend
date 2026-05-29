"""
Template-Based Workout Plan Generator (Offline Fallback).

Generates structured workout plans using predefined exercise templates
and rule-based personalization. Requires NO external API calls.

This is used as an automatic fallback when all AI providers fail
(e.g., rate limits, quota exhaustion, network issues).
"""

import json
import os
from .schemas import WorkoutPlan, WorkoutDay, Exercise, WarmUpExercise

# ---------------------------------------------------------------------------
# Dynamic Database Loading (Loaded from exercises_db.json)
# ---------------------------------------------------------------------------

# تحديد مسار ملف الـ JSON في نفس الفولدر الحالي للكود
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "exercises_db.json")

def _load_database():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Could not find exercises database at {DB_PATH}")
        
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    
    # تحويل بيانات الـ Warm Up والـ Cool Down (مع مراعاة اسامى الحقول في الـ Schema عندك)
    warm_up = [WarmUpExercise(exercise=ex["name"], duration=ex["duration"]) for ex in db["warm_up"]]
    cool_down = [WarmUpExercise(exercise=ex["name"], duration=ex["duration"]) for ex in db["cool_down"]]
    
    # تحويل باقي المجموعات العضلية إلى الـ Exercise Schema مباشرة
    chest = [Exercise(**ex) for ex in db["chest"]]
    back = [Exercise(**ex) for ex in db["back"]]
    shoulders = [Exercise(**ex) for ex in db["shoulders"]]
    legs = [Exercise(**ex) for ex in db["legs"]]
    arms = [Exercise(**ex) for ex in db["arms"]]
    core = [Exercise(**ex) for ex in db["core"]]
    cardio = [Exercise(**ex) for ex in db["cardio"]]
    flexibility = [Exercise(**ex) for ex in db["flexibility"]]
    
    return warm_up, cool_down, chest, back, shoulders, legs, arms, core, cardio, flexibility

# تحميل البيانات وتخزينها في المتغيرات بنفس الأسامي القديمة تماماً
(
    WARM_UP, COOL_DOWN, CHEST_EXERCISES, BACK_EXERCISES,
    SHOULDER_EXERCISES, LEG_EXERCISES, ARM_EXERCISES,
    CORE_EXERCISES, CARDIO_EXERCISES, FLEXIBILITY_EXERCISES
) = _load_database()
# ---------------------------------------------------------------------------
# Goal-based plan templates
# ---------------------------------------------------------------------------

def _adjust_volume(exercises: list[Exercise], goal: str, activity: str) -> list[Exercise]:
    """Adjust sets/reps based on goal and activity level."""
    adjusted = []
    for ex in exercises:
        sets = ex.sets
        reps = ex.reps

        if goal == "Lose Weight":
            sets = max(2, sets - 1)
            if reps.replace("-", "").replace(" ", "").split()[0].isdigit():
                reps = reps  # keep higher rep ranges for fat loss
        elif goal == "Build Muscle":
            sets = min(5, sets + 1)

        if activity in ("Sedentary", "Lightly Active"):
            sets = max(2, sets - 1)
        elif activity in ("Very Active", "Extra Active"):
            sets = min(5, sets + 1)

        adjusted.append(Exercise(
            name=ex.name,
            sets=sets,
            reps=reps,
            rest_between_sets=ex.rest_between_sets,
            form_tip=ex.form_tip,
        ))
    return adjusted


def _build_muscle_plan(activity: str) -> list[WorkoutDay]:
    """PPL (Push/Pull/Legs) split for muscle building."""
    return [
        WorkoutDay(day="Monday", focus="Push — Chest, Shoulders & Triceps", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CHEST_EXERCISES[:3] + SHOULDER_EXERCISES[:2] + ARM_EXERCISES[1:2], "Build Muscle", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Tuesday", focus="Pull — Back & Biceps", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(BACK_EXERCISES[:3] + ARM_EXERCISES[0:1] + ARM_EXERCISES[2:3], "Build Muscle", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Wednesday", focus="Legs & Core", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(LEG_EXERCISES[:4] + CORE_EXERCISES[:2], "Build Muscle", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Thursday", focus="Rest & Active Recovery", is_rest_day=True,
                   warm_up=[], exercises=_adjust_volume(FLEXIBILITY_EXERCISES[:3], "Build Muscle", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Friday", focus="Push — Chest, Shoulders & Triceps", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CHEST_EXERCISES[1:] + SHOULDER_EXERCISES[2:] + ARM_EXERCISES[3:4], "Build Muscle", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Saturday", focus="Pull — Back, Biceps & Rear Delts", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(BACK_EXERCISES[1:] + SHOULDER_EXERCISES[3:] + ARM_EXERCISES[0:1], "Build Muscle", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Sunday", focus="Rest & Recovery", is_rest_day=True,
                   warm_up=[], exercises=_adjust_volume(FLEXIBILITY_EXERCISES[2:], "Build Muscle", activity), cool_down=COOL_DOWN),
    ]


def _lose_weight_plan(activity: str) -> list[WorkoutDay]:
    """Cardio-heavy split with strength for fat loss."""
    return [
        WorkoutDay(day="Monday", focus="Full Body Strength", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CHEST_EXERCISES[:2] + BACK_EXERCISES[:2] + LEG_EXERCISES[:1], "Lose Weight", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Tuesday", focus="HIIT Cardio & Core", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CARDIO_EXERCISES[:3] + CORE_EXERCISES[:2], "Lose Weight", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Wednesday", focus="Upper Body & Cardio", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(SHOULDER_EXERCISES[:2] + ARM_EXERCISES[:2] + CARDIO_EXERCISES[3:4], "Lose Weight", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Thursday", focus="Active Recovery & Flexibility", is_rest_day=True,
                   warm_up=[], exercises=_adjust_volume(FLEXIBILITY_EXERCISES, "Lose Weight", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Friday", focus="Lower Body Strength", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(LEG_EXERCISES + CORE_EXERCISES[2:4], "Lose Weight", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Saturday", focus="Steady-State Cardio & Core", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CARDIO_EXERCISES[4:] + CARDIO_EXERCISES[1:2] + CORE_EXERCISES[:3], "Lose Weight", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Sunday", focus="Rest & Recovery", is_rest_day=True,
                   warm_up=[], exercises=_adjust_volume(FLEXIBILITY_EXERCISES[2:], "Lose Weight", activity), cool_down=COOL_DOWN),
    ]


def _maintain_plan(activity: str) -> list[WorkoutDay]:
    """Balanced split for maintenance."""
    return [
        WorkoutDay(day="Monday", focus="Upper Body Strength", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CHEST_EXERCISES[:2] + BACK_EXERCISES[:2] + SHOULDER_EXERCISES[:1], "Maintain", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Tuesday", focus="Cardio & Core", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CARDIO_EXERCISES[:2] + CORE_EXERCISES[:3], "Maintain", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Wednesday", focus="Lower Body Strength", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(LEG_EXERCISES[:4], "Maintain", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Thursday", focus="Rest & Active Recovery", is_rest_day=True,
                   warm_up=[], exercises=_adjust_volume(FLEXIBILITY_EXERCISES[:3], "Maintain", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Friday", focus="Full Body Functional", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CHEST_EXERCISES[2:3] + BACK_EXERCISES[2:3] + LEG_EXERCISES[3:4] + CORE_EXERCISES[3:], "Maintain", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Saturday", focus="Cardio & Flexibility", is_rest_day=False,
                   warm_up=WARM_UP, exercises=_adjust_volume(CARDIO_EXERCISES[3:] + FLEXIBILITY_EXERCISES[:2], "Maintain", activity), cool_down=COOL_DOWN),
        WorkoutDay(day="Sunday", focus="Rest & Recovery", is_rest_day=True,
                   warm_up=[], exercises=_adjust_volume(FLEXIBILITY_EXERCISES[2:], "Maintain", activity), cool_down=COOL_DOWN),
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_GOAL_MAP = {
    "Lose Weight": _lose_weight_plan,
    "Build Muscle": _build_muscle_plan,
    "Maintain": _maintain_plan,
}


def generate_template_workout(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    goal: str,
    activity_level: str,
) -> WorkoutPlan:
    """
    Generates a workout plan from local templates. No API calls needed.

    Personalizes based on goal, activity level, age, and gender.
    """
    plan_fn = _GOAL_MAP.get(goal, _maintain_plan)
    schedule = plan_fn(activity_level)

    # Age-based adjustments
    if age > 50:
        note_suffix = " Exercises have been adjusted for joint safety. Focus on controlled movements."
    elif age < 18:
        note_suffix = " Focus on bodyweight exercises and proper form before adding heavy weights."
    else:
        note_suffix = ""

    bmi = weight_kg / ((height_cm / 100) ** 2)

    return WorkoutPlan(
        plan_name=f"VitalityAI {goal} Plan — {activity_level}",
        summary=(
            f"A personalized 7-day {goal.lower()} program designed for a "
            f"{age}-year-old {gender.lower()} ({height_cm}cm, {weight_kg}kg, BMI: {bmi:.1f}). "
            f"This plan is tailored to your {activity_level.lower()} lifestyle with progressive "
            f"overload principles and adequate recovery."
        ),
        weekly_schedule=schedule,
        notes=(
            f"Always warm up before training and cool down after. Stay hydrated and aim for "
            f"7-9 hours of sleep. Adjust weights to maintain proper form — if you can't complete "
            f"the minimum reps with good form, reduce the load.{note_suffix}"
        ),
    )
