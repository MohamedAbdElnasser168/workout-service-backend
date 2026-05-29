"""
FastAPI Application Factory.

Creates and configures the FastAPI app with CORS, middleware, and route inclusion.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import workout_router
from api.middleware.error_handler import GlobalErrorHandlerMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    logging.getLogger(__name__).info("VitalityAI Workout Service starting up...")
    yield
    logging.getLogger(__name__).info("VitalityAI Workout Service shutting down...")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="VitalityAI - Workout Plan Service",
        description="AI-powered personalized workout plan generation API.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GlobalErrorHandlerMiddleware)

    # --- Routes ---
    app.include_router(workout_router)

    return app


app = create_app()
