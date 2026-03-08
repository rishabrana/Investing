"""Watchlist management endpoints."""

import time
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from storage.json_store import JsonStore, Watchlist, WatchlistEntry
from clients.polygon_client import PolygonClient
from clients.sec_edgar_client import SECEdgarClient
from backend.api.dependencies import get_json_store, get_polygon_client, get_sec_edgar_client
from backend.models.requests import (
    AddTickerRequest,
    ValidateTickerRequest,
    ValidateTickersBatchRequest,
    AddTickersBatchRequest,
)
from backend.models.responses import (
    WatchlistResponse,
    TickerEntryResponse,
    AddTickerResponse,
    ValidateTickerResponse,
    ValidateTickersBatchResponse,
    AddTickerBatchResult,
    AddTickersBatchResponse,
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
def add_ticker(
    request: AddTickerRequest,
    store: JsonStore = Depends(get_json_store),
    polygon_client: Optional[PolygonClient] = Depends(get_polygon_client)
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

    # Silently skip if already exists
    existing = next((entry for entry in watchlist.tickers if entry.symbol == symbol), None)
    if existing:
        return AddTickerResponse(
            success=True,
            message=f"{symbol} is already in the watchlist",
            entry=_watchlist_entry_to_response(existing)
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
    Remove a ticker from the watchlist and delete all associated data.

    This will:
    1. Remove the ticker from the watchlist
    2. Delete all raw data (latest and historical)
    3. Delete all metrics data (latest and historical)

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

    # Save updated watchlist
    store.save_watchlist(watchlist, name="default")

    # Delete all data for this ticker (raw and metrics)
    store.delete_ticker_data(symbol)

    return RemoveTickerResponse(
        success=True,
        message=f"Removed {symbol} from watchlist and deleted all associated data"
    )


def _validate_ticker_with_fallback(
    symbol: str,
    polygon_client: Optional[PolygonClient],
    sec_client: SECEdgarClient,
) -> ValidateTickerResponse:
    """
    Validate a ticker using Polygon (primary) with SEC EDGAR fallback.

    Falls back to SEC EDGAR when:
    - No Polygon API key configured
    - Polygon returns a rate limit error
    - Polygon returns a non-404 error
    """
    # Try Polygon first (has company names like "Apple Inc.")
    if polygon_client is not None:
        is_valid, company_name, error = polygon_client.validate_ticker(symbol)
        if is_valid:
            return ValidateTickerResponse(
                is_valid=True,
                symbol=symbol,
                company_name=company_name,
                error=None,
            )
        # Only trust a 404 as "definitely invalid"
        if "does not exist" in error:
            return ValidateTickerResponse(
                is_valid=False,
                symbol=symbol,
                company_name=None,
                error=error,
            )
        # For rate limits or other errors, fall through to SEC EDGAR

    # Fallback: SEC EDGAR (free, no rate limit issues for validation)
    is_valid, company_name, error = sec_client.validate_ticker(symbol)
    return ValidateTickerResponse(
        is_valid=is_valid,
        symbol=symbol,
        company_name=company_name if is_valid else None,
        error=error if not is_valid else None,
    )


@router.post("/validate", response_model=ValidateTickerResponse)
def validate_ticker(
    request: ValidateTickerRequest,
    polygon_client: Optional[PolygonClient] = Depends(get_polygon_client),
    sec_client: SECEdgarClient = Depends(get_sec_edgar_client),
):
    """Validate a single ticker symbol."""
    symbol = request.symbol.upper()
    return _validate_ticker_with_fallback(symbol, polygon_client, sec_client)


@router.post("/validate-batch", response_model=ValidateTickersBatchResponse)
def validate_tickers_batch(
    request: ValidateTickersBatchRequest,
    store: JsonStore = Depends(get_json_store),
    polygon_client: Optional[PolygonClient] = Depends(get_polygon_client),
    sec_client: SECEdgarClient = Depends(get_sec_edgar_client),
):
    """
    Validate multiple ticker symbols at once.

    - Duplicates (already in watchlist) are skipped and marked valid.
    - Uses Polygon.io with SEC EDGAR fallback for validation.
    """
    results: List[ValidateTickerResponse] = []
    valid_count = 0
    invalid_count = 0

    # Load existing watchlist for duplicate detection
    watchlist = store.load_watchlist("default")
    existing_symbols = (
        {entry.symbol for entry in watchlist.tickers} if watchlist else set()
    )

    for symbol in request.symbols:
        symbol = symbol.strip().upper()
        if not symbol:
            continue

        # Skip duplicates — mark as valid so UI can proceed
        if symbol in existing_symbols:
            results.append(ValidateTickerResponse(
                is_valid=True,
                symbol=symbol,
                company_name=None,
                error="already_in_watchlist",
            ))
            valid_count += 1
            continue

        # Brief pause between Polygon calls to reduce rate limiting
        if polygon_client and results:
            time.sleep(0.3)

        result = _validate_ticker_with_fallback(symbol, polygon_client, sec_client)
        results.append(result)
        if result.is_valid:
            valid_count += 1
        else:
            invalid_count += 1

    return ValidateTickersBatchResponse(
        results=results,
        valid_count=valid_count,
        invalid_count=invalid_count,
    )


@router.post("/add-batch", response_model=AddTickersBatchResponse)
def add_tickers_batch(
    request: AddTickersBatchRequest,
    store: JsonStore = Depends(get_json_store),
    polygon_client: Optional[PolygonClient] = Depends(get_polygon_client)
):
    """
    Add multiple tickers to the watchlist at once.

    Args:
        request: AddTickersBatchRequest with list of symbols

    Returns:
        AddTickersBatchResponse with results for each symbol
    """
    results: List[AddTickerBatchResult] = []
    added_count = 0
    failed_count = 0
    skipped_count = 0

    watchlist = store.load_watchlist("default")
    if watchlist is None:
        watchlist = Watchlist(tickers=[])

    existing_symbols = {entry.symbol for entry in watchlist.tickers}

    for symbol in request.symbols:
        # Clean and normalize the symbol
        symbol = symbol.strip().upper()

        if not symbol:
            continue

        # Silently skip if already exists
        if symbol in existing_symbols:
            results.append(AddTickerBatchResult(
                symbol=symbol,
                success=True,
                message=f"{symbol} is already in the watchlist",
            ))
            skipped_count += 1
            continue

        # Validate ticker if not skipped
        company_name = symbol
        if not request.skip_validation and polygon_client:
            is_valid, validated_name, error = polygon_client.validate_ticker(symbol)
            if not is_valid:
                results.append(AddTickerBatchResult(
                    symbol=symbol,
                    success=False,
                    message=f"Invalid ticker: {symbol}",
                    error=error or "Validation failed"
                ))
                failed_count += 1
                continue
            if validated_name:
                company_name = validated_name

        # Create entry
        entry = WatchlistEntry(
            symbol=symbol,
            name=company_name,
            notes=None,
            metrics_profile=None,
            custom_fields={}
        )

        watchlist.tickers.append(entry)
        existing_symbols.add(symbol)

        results.append(AddTickerBatchResult(
            symbol=symbol,
            success=True,
            message=f"Added {symbol} to watchlist",
            company_name=company_name
        ))
        added_count += 1

    # Save watchlist if any were added
    if added_count > 0:
        store.save_watchlist(watchlist, name="default")

    return AddTickersBatchResponse(
        results=results,
        added_count=added_count,
        failed_count=failed_count,
        skipped_count=skipped_count
    )
