"""Watchlist management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from storage.json_store import JsonStore, Watchlist, WatchlistEntry
from clients.polygon_client import PolygonClient
from backend.api.dependencies import get_json_store, get_polygon_client
from backend.models.requests import AddTickerRequest, ValidateTickerRequest
from backend.models.responses import (
    WatchlistResponse,
    TickerEntryResponse,
    AddTickerResponse,
    ValidateTickerResponse,
    RemoveTickerResponse,
)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def _watchlist_entry_to_response(entry: WatchlistEntry) -> TickerEntryResponse:
    """Convert WatchlistEntry to TickerEntryResponse."""
    return TickerEntryResponse(
        symbol=entry.symbol,
        name=entry.name,
        notes=entry.notes,
        metrics_profile=entry.metrics_profile,
    )


@router.get("", response_model=WatchlistResponse)
async def get_watchlist(
    name: str = "default",
    store: JsonStore = Depends(get_json_store)
):
    """
    Get watchlist with all tickers.

    Args:
        name: Watchlist name (default: "default")

    Returns:
        WatchlistResponse with all tickers
    """
    watchlist = store.load_watchlist(name)

    if watchlist is None:
        # Return empty watchlist if not found
        watchlist = Watchlist(tickers=[])

    return WatchlistResponse(
        name=name,
        default_metrics_profile=watchlist.default_metrics_profile,
        tickers=[_watchlist_entry_to_response(entry) for entry in watchlist.tickers],
        total_count=len(watchlist.tickers)
    )


@router.post("/add", response_model=AddTickerResponse)
async def add_ticker(
    request: AddTickerRequest,
    store: JsonStore = Depends(get_json_store),
    polygon_client: PolygonClient | None = Depends(get_polygon_client)
):
    """
    Add a ticker to the watchlist.

    Args:
        request: AddTickerRequest with symbol, name, notes

    Returns:
        AddTickerResponse with success status
    """
    symbol = request.symbol.upper()
    watchlist = store.load_watchlist("default")

    if watchlist is None:
        watchlist = Watchlist(tickers=[])

    # Check if already exists
    if any(entry.symbol == symbol for entry in watchlist.tickers):
        raise HTTPException(
            status_code=400,
            detail=f"{symbol} is already in the watchlist"
        )

    # Validate ticker if not skipped
    company_name = request.name or symbol
    if not request.skip_validation and polygon_client:
        is_valid, validated_name, error = polygon_client.validate_ticker(symbol)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=error or f"Invalid ticker: {symbol}"
            )
        if not request.name and validated_name:
            company_name = validated_name

    # Create entry
    entry = WatchlistEntry(
        symbol=symbol,
        name=company_name,
        notes=request.notes,
        metrics_profile=None,
        custom_fields={}
    )

    watchlist.tickers.append(entry)
    store.save_watchlist(watchlist, name="default")

    return AddTickerResponse(
        success=True,
        message=f"Added {symbol} to watchlist",
        entry=_watchlist_entry_to_response(entry)
    )


@router.delete("/{symbol}", response_model=RemoveTickerResponse)
async def remove_ticker(
    symbol: str,
    store: JsonStore = Depends(get_json_store)
):
    """
    Remove a ticker from the watchlist.

    Args:
        symbol: Ticker symbol to remove

    Returns:
        RemoveTickerResponse with success status
    """
    symbol = symbol.upper()
    watchlist = store.load_watchlist("default")

    if watchlist is None:
        raise HTTPException(
            status_code=404,
            detail="Watchlist not found"
        )

    # Filter out the ticker
    original_count = len(watchlist.tickers)
    watchlist.tickers = [
        entry for entry in watchlist.tickers
        if entry.symbol != symbol
    ]

    if len(watchlist.tickers) == original_count:
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} not found in watchlist"
        )

    store.save_watchlist(watchlist, name="default")

    return RemoveTickerResponse(
        success=True,
        message=f"Removed {symbol} from watchlist"
    )


@router.post("/validate", response_model=ValidateTickerResponse)
async def validate_ticker(
    request: ValidateTickerRequest,
    polygon_client: PolygonClient | None = Depends(get_polygon_client)
):
    """
    Validate a ticker symbol.

    Args:
        request: ValidateTickerRequest with symbol

    Returns:
        ValidateTickerResponse with validation result
    """
    symbol = request.symbol.upper()

    if polygon_client is None:
        # No API key, skip validation
        return ValidateTickerResponse(
            is_valid=True,
            symbol=symbol,
            company_name=None,
            error=None
        )

    is_valid, company_name, error = polygon_client.validate_ticker(symbol)

    return ValidateTickerResponse(
        is_valid=is_valid,
        symbol=symbol,
        company_name=company_name if is_valid else None,
        error=error if not is_valid else None
    )
