"""
Health Probe Endpoint (GET /api/health) per PRD §9 & §12.
"""
import time
from fastapi import APIRouter, Response, status
from app.core.config import settings
from app.db.session import db_manager

router = APIRouter(tags=["Health"])
start_time = time.time()


@router.get("/health")
async def get_health(response: Response):
    """System health check endpoint verifying database connectivity and pgvector status."""
    db_health = await db_manager.check_health()
    uptime_seconds = round(time.time() - start_time, 2)

    db_connected = db_health.get("connected", False)
    pgvector_ok = db_health.get("pgvector", False)

    if not db_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        overall_status = "unhealthy"
        db_status = "disconnected"
    elif not pgvector_ok:
        response.status_code = status.HTTP_200_OK
        overall_status = "degraded"
        db_status = "connected"
    else:
        response.status_code = status.HTTP_200_OK
        overall_status = "healthy"
        db_status = "connected"

    db_dep = {
        "status": db_status,
        "latency_ms": db_health.get("latency_ms"),
    }
    if db_health.get("error"):
        db_dep["error"] = db_health.get("error")

    pgvector_dep = {
        "status": "available" if pgvector_ok else "unavailable",
    }
    if db_health.get("pgvector_version"):
        pgvector_dep["version"] = db_health.get("pgvector_version")

    return {
        "status": overall_status,
        "database": db_status,
        "vector_store": settings.VECTOR_STORE_BACKEND,
        "uptime_seconds": uptime_seconds,
        "version": settings.VERSION,
        "dependencies": {
            "database": db_dep,
            "pgvector": pgvector_dep,
        },
    }
