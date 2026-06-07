"""
Global Error Handling Middleware.

Catches unhandled exceptions and AI validation errors, returning
consistent JSON error responses to the client.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class GlobalErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catches unhandled exceptions and returns structured JSON errors."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except Exception as e:
            logger.exception("Unhandled server error: %s", e)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An internal server error occurred.",
                    "detail": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
                },
            )
