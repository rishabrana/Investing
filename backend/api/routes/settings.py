"""Settings management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

from storage.json_store import JsonStore
from backend.api.dependencies import get_json_store

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/api-keys")
async def get_api_keys(store: JsonStore = Depends(get_json_store)) -> Dict[str, str]:
    """
    Get all stored API keys (masked for security).

    Returns:
        Dict mapping provider name to masked API key
    """
    keys = store.load_api_keys()
    # Mask the keys for security - show only first 4 and last 4 characters
    masked_keys = {}
    for provider, key in keys.items():
        if len(key) > 8:
            masked_keys[provider] = f"{key[:4]}...{key[-4:]}"
        else:
            masked_keys[provider] = "****"

    return masked_keys


@router.post("/api-keys")
async def save_api_keys(
    keys: Dict[str, str],
    store: JsonStore = Depends(get_json_store)
) -> Dict[str, str]:
    """
    Save API keys for multiple providers.

    Args:
        keys: Dict mapping provider name to API key

    Returns:
        Success message
    """
    for provider, key in keys.items():
        if key and key.strip():
            store.save_api_key(provider, key.strip())

    return {"message": "API keys saved successfully"}


@router.delete("/api-keys/{provider}")
async def delete_api_key(
    provider: str,
    store: JsonStore = Depends(get_json_store)
) -> Dict[str, str]:
    """
    Delete API key for a specific provider.

    Args:
        provider: Provider identifier

    Returns:
        Success message
    """
    deleted = store.delete_api_key(provider)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"No API key found for provider: {provider}"
        )

    return {"message": f"API key for {provider} deleted successfully"}
