"""
FetchResult - Encapsulates the outcome of a data fetch for a ticker.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from storage.json_store import RawSnapshot


class FetchResult:
    """Result of fetching data for a single ticker."""

    def __init__(
        self,
        ticker: str,
        success: bool,
        snapshot: Optional[RawSnapshot] = None,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        fields_fetched: Optional[Set[str]] = None,
        fields_missing: Optional[Set[str]] = None,
        providers_used: Optional[Dict[str, int]] = None,
    ):
        self.ticker = ticker
        self.success = success
        self.snapshot = snapshot
        self.errors = errors or []
        self.warnings = warnings or []
        self.fields_fetched = fields_fetched or set()
        self.fields_missing = fields_missing or set()
        self.providers_used = providers_used or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/reporting."""
        return {
            "ticker": self.ticker,
            "success": self.success,
            "fields_fetched": len(self.fields_fetched),
            "fields_missing": len(self.fields_missing),
            "errors": self.errors,
            "warnings": self.warnings,
            "providers_used": self.providers_used,
        }


__all__ = ["FetchResult"]
