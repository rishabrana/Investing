"""Pydantic models for API requests and responses."""

from backend.models.requests import (
    AddTickerRequest,
    ValidateTickerRequest,
    ValidateTickersBatchRequest,
    AddTickersBatchRequest,
    RefreshStockRequest,
    RefreshWatchlistRequest,
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
    StockOverviewResponse,
    StockMetricsResponse,
    StockHistoryResponse,
    RefreshStockResponse,
    RefreshWatchlistResponse,
)

__all__ = [
    # Requests
    "AddTickerRequest",
    "ValidateTickerRequest",
    "ValidateTickersBatchRequest",
    "AddTickersBatchRequest",
    "RefreshStockRequest",
    "RefreshWatchlistRequest",
    # Responses
    "WatchlistResponse",
    "TickerEntryResponse",
    "AddTickerResponse",
    "ValidateTickerResponse",
    "ValidateTickersBatchResponse",
    "AddTickerBatchResult",
    "AddTickersBatchResponse",
    "RemoveTickerResponse",
    "StockOverviewResponse",
    "StockMetricsResponse",
    "StockHistoryResponse",
    "RefreshStockResponse",
    "RefreshWatchlistResponse",
]
