"""Alpha Vantage API client for financial data."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Set, Tuple

import requests


logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """Lightweight Alpha Vantage REST client."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str, session: requests.Session | None = None):
        if not api_key:
            raise ValueError("Alpha Vantage API key is required")
        self.api_key = api_key
        self.session = session or requests.Session()

    def fetch_fields(
        self,
        ticker: str,
        fields: Iterable[str],
        period: str = "annual",
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str], list[str]]:
        """
        Fetch the requested fields from Alpha Vantage.

        Args:
            ticker: Stock ticker symbol
            fields: Field IDs to fetch
            period: "annual" or "quarterly"

        Returns:
            Tuple of (data, source_metadata, fetched_fields, warnings)
        """
        ticker = ticker.upper()
        requested = set(fields)
        data: Dict[str, Any] = {
            "price": {},
            "market_data": {},
            "financials": {},
            "cash_flow": {},
        }
        source_metadata: Dict[str, Any] = {}
        fetched: Set[str] = set()
        warnings: list[str] = []

        # Determine which statements we need
        need_income_statement = any(
            f in requested
            for f in [
                "financials.interest_expense",
                "financials.depreciation_amortization",
                "financials.ebitda",
            ]
        )
        need_balance_sheet = any(
            f in requested for f in ["financials.retained_earnings"]
        )

        try:
            if need_income_statement:
                fetched |= self._fetch_income_statement(
                    ticker, requested, data, source_metadata
                )
        except Exception as exc:
            msg = f"Alpha Vantage income statement fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        try:
            if need_balance_sheet:
                fetched |= self._fetch_balance_sheet(
                    ticker, requested, data, source_metadata
                )
        except Exception as exc:
            msg = f"Alpha Vantage balance sheet fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        return data, source_metadata, fetched, warnings

    def _make_request(self, params: Dict[str, Any]) -> dict:
        """Make API request to Alpha Vantage."""
        params = params.copy()
        params["apikey"] = self.api_key
        response = self.session.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        # Check for API error messages
        if "Error Message" in payload:
            raise RuntimeError(f"API Error: {payload['Error Message']}")
        if "Note" in payload:
            raise RuntimeError(f"API Rate Limit: {payload['Note']}")

        return payload

    def _fetch_income_statement(
        self,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        """Fetch income statement data."""
        payload = self._make_request(
            {"function": "INCOME_STATEMENT", "symbol": ticker}
        )

        annual_reports = payload.get("annualReports", [])
        if not annual_reports:
            raise RuntimeError("No annual income statement data available")

        # Get most recent report
        report = annual_reports[0]

        # Map Alpha Vantage fields to our schema
        mapping = {
            "financials.interest_expense": report.get("interestExpense"),
            "financials.depreciation_amortization": report.get(
                "depreciationAndAmortization"
            ),
            "financials.ebitda": report.get("ebitda"),
        }

        fetched: Set[str] = set()
        for field, value in mapping.items():
            if value is not None and value != "None" and field in requested:
                try:
                    # Convert to float
                    numeric_value = float(value)
                    section, key = field.split(".", 1)
                    data["financials"][key] = numeric_value
                    metadata[field] = {
                        "provider": "alpha_vantage",
                        "timestamp": report.get("fiscalDateEnding"),
                        "endpoint": "INCOME_STATEMENT",
                    }
                    fetched.add(field)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {field} value: {value}")

        return fetched

    def _fetch_balance_sheet(
        self,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        """Fetch balance sheet data."""
        payload = self._make_request(
            {"function": "BALANCE_SHEET", "symbol": ticker}
        )

        annual_reports = payload.get("annualReports", [])
        if not annual_reports:
            raise RuntimeError("No annual balance sheet data available")

        # Get most recent report
        report = annual_reports[0]

        mapping = {
            "financials.retained_earnings": report.get("retainedEarnings"),
        }

        fetched: Set[str] = set()
        for field, value in mapping.items():
            if value is not None and value != "None" and field in requested:
                try:
                    numeric_value = float(value)
                    section, key = field.split(".", 1)
                    data["financials"][key] = numeric_value
                    metadata[field] = {
                        "provider": "alpha_vantage",
                        "timestamp": report.get("fiscalDateEnding"),
                        "endpoint": "BALANCE_SHEET",
                    }
                    fetched.add(field)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {field} value: {value}")

        return fetched
