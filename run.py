"""
Application Entry Point.

Run with: python run.py
Or with: uvicorn api.main:app --reload
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info",
    )
