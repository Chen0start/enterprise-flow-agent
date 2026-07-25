from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise knowledge retrieval and workflow agent backend",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    """Return basic service information."""

    return {
        "message": "EnterpriseFlow Agent API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
