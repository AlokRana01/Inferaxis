"""Health check endpoints for system monitoring."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.database import check_db_connection

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=dict[str, Any])
@router.get("/api/health", response_model=dict[str, Any])
async def health_check() -> dict[str, Any]:
    """Return application operational status and database connection state."""
    db_connected = await check_db_connection()

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_connected else "unreachable",
        "timestamp": datetime.now(UTC).isoformat(),
    }
