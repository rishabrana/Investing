"""Pydantic models for API request bodies."""

from typing import Optional
from pydantic import BaseModel, Field


class AddTickerRequest(BaseModel):
    """Request to add a ticker to the watchlist."""

    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    name: Optional[str] = Field(None, description="Company name (auto-fetched if not provided)")
    notes: Optional[str] = Field(None, description="Optional notes about this stock")
    skip_validation: bool = Field(False, description="Skip ticker validation")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "notes": "Great business, expensive valuation",
                "skip_validation": False
            }
        }


class ValidateTickerRequest(BaseModel):
    """Request to validate a ticker symbol."""

    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol to validate")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL"
            }
        }


class RefreshStockRequest(BaseModel):
    """Request to refresh stock data."""

    force: bool = Field(False, description="Force refresh even if recent data exists")

    class Config:
        json_schema_extra = {
            "example": {
                "force": True
            }
        }


class RefreshWatchlistRequest(BaseModel):
    """Request to refresh all stocks in watchlist."""

    watchlist: str = Field("default", description="Watchlist name to refresh")
    force: bool = Field(False, description="Force refresh even if recent data exists")

    class Config:
        json_schema_extra = {
            "example": {
                "watchlist": "default",
                "force": False
            }
        }
