"""Health check endpoints."""

from fastapi import APIRouter, Depends
from storage.json_store import JsonStore
from backend.api.dependencies import get_json_store

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "service": "Investment Analysis API",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check(store: JsonStore = Depends(get_json_store)):
    """
    Readiness check - verifies dependencies are available.

    Returns:
        Readiness status with dependency checks
    """
    checks = {
        "json_store": False,
        "api_keys": {}
    }

    # Check if JsonStore is accessible
    try:
        # Try to load watchlist (creates empty if not exists)
        watchlist = store.load_watchlist("default")
        checks["json_store"] = True
    except Exception:
        checks["json_store"] = False

    # Check API keys
    for provider in ["polygon.io", "alpha_vantage"]:
        api_key = store.get_api_key(provider)
        checks["api_keys"][provider] = api_key is not None

    all_ready = checks["json_store"]

    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks
    }
