"""Pydantic models for API responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TickerEntryResponse(BaseModel):
    """Individual ticker entry in watchlist."""

    symbol: str
    name: Optional[str] = None
    notes: Optional[str] = None
    metrics_profile: Optional[str] = None


class WatchlistResponse(BaseModel):
    """Response for GET /watchlist."""

    name: str
    default_metrics_profile: str
    tickers: List[TickerEntryResponse]
    total_count: int


class AddTickerResponse(BaseModel):
    """Response for POST /watchlist/add."""

    success: bool
    message: str
    entry: TickerEntryResponse


class ValidateTickerResponse(BaseModel):
    """Response for POST /watchlist/validate."""

    is_valid: bool
    symbol: str
    company_name: Optional[str] = None
    error: Optional[str] = None


class RemoveTickerResponse(BaseModel):
    """Response for DELETE /watchlist/{symbol}."""

    success: bool
    message: str


class PriceData(BaseModel):
    """Stock price information."""

    close: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    as_of: str


class MarketData(BaseModel):
    """Market data information."""

    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None


class StockOverviewResponse(BaseModel):
    """Response for GET /stocks/{ticker}/overview."""

    ticker: str
    name: Optional[str] = None
    price: PriceData
    market_data: MarketData


class StockMetricsResponse(BaseModel):
    """Response for GET /stocks/{ticker}/metrics."""

    ticker: str
    as_of: str
    calculated_at: str
    profile_used: str
    valuation: Dict[str, Any] = Field(default_factory=dict)
    profitability: Dict[str, Any] = Field(default_factory=dict)
    cash_generation: Dict[str, Any] = Field(default_factory=dict)
    financial_strength: Dict[str, Any] = Field(default_factory=dict)
    capital_allocation: Dict[str, Any] = Field(default_factory=dict)
    moat: Dict[str, Any] = Field(default_factory=dict)
    growth: Dict[str, Any] = Field(default_factory=dict)


class HistoryDataPoint(BaseModel):
    """Single data point in historical series."""

    period: str
    value: Optional[float] = None


class StockHistoryResponse(BaseModel):
    """Response for GET /stocks/{ticker}/history."""

    ticker: str
    metric: str
    data_points: List[HistoryDataPoint]


class RefreshStockResponse(BaseModel):
    """Response for POST /stocks/{ticker}/refresh."""

    success: bool
    ticker: str
    fields_fetched: int
    fields_missing: int
    timestamp: str
    providers_used: Dict[str, int] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class RefreshResult(BaseModel):
    """Individual stock refresh result."""

    ticker: str
    success: bool
    fields_fetched: int
    fields_missing: int = 0
    errors: List[str] = Field(default_factory=list)


class RefreshWatchlistResponse(BaseModel):
    """Response for POST /stocks/refresh-watchlist."""

    success: bool
    processed: int
    successful: int
    failed: int
    results: List[RefreshResult]
