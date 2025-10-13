"""Polygon.io API client wrapped for DataSourceRouter usage."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Set, Tuple

import requests


logger = logging.getLogger(__name__)


class PolygonClient:
    """Lightweight Polygon.io REST client."""

    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: str, session: requests.Session | None = None):
        if not api_key:
            raise ValueError("Polygon API key is required")
        self.api_key = api_key
        self.session = session or requests.Session()

    # -------- public API --------

    def validate_ticker(self, ticker: str) -> Tuple[bool, str, str]:
        """
        Validate if a ticker symbol exists and get company name.

        Args:
            ticker: Stock ticker symbol to validate

        Returns:
            Tuple of (is_valid, company_name, error_message)
            - is_valid: True if ticker exists
            - company_name: Company name if found, empty string otherwise
            - error_message: Error description if validation fails
        """
        ticker = ticker.upper()
        try:
            payload = self._make_request(f"/v3/reference/tickers/{ticker}")
            result = payload.get("results") or {}

            if not result:
                return False, "", f"Ticker '{ticker}' not found"

            company_name = result.get("name", ticker)
            return True, company_name, ""

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return False, "", f"Ticker '{ticker}' does not exist"
            return False, "", f"API error: {str(e)}"
        except Exception as e:
            return False, "", f"Validation failed: {str(e)}"

    def fetch_fields(
        self,
        ticker: str,
        fields: Iterable[str],
        period: str = "annual",
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str], list[str]]:
        """Fetch the requested fields and return normalized payload."""

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

        try:
            if any(f.startswith("price.") for f in requested):
                fetched |= self._fetch_price(ticker, requested, data, source_metadata)
        except Exception as exc:  # pragma: no cover - network failures
            msg = f"Polygon price fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        try:
            if any(f.startswith("market_data.") for f in requested):
                fetched |= self._fetch_ticker_details(
                    ticker, requested, data, source_metadata
                )
        except Exception as exc:  # pragma: no cover - network failures
            msg = f"Polygon ticker details fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        try:
            needed_financial_fields = {
                field
                for field in requested
                if field.startswith("financials.")
                or field.startswith("cash_flow.")
            }
            if needed_financial_fields:
                fetched |= self._fetch_financials(
                    ticker,
                    needed_financial_fields,
                    period,
                    data,
                    source_metadata,
                )
        except Exception as exc:  # pragma: no cover - network failures
            msg = f"Polygon financials fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        return data, source_metadata, fetched, warnings

    # -------- internal helpers --------

    def _make_request(self, path: str, params: Dict[str, Any] | None = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        params = params.copy() if params else {}
        params["apiKey"] = self.api_key
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if "status" in payload and payload["status"] != "OK":
            raise RuntimeError(payload)
        return payload

    def _fetch_price(
        self,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        payload = self._make_request(f"/v2/aggs/ticker/{ticker}/prev")
        results = payload.get("results") or []
        if not results:
            raise RuntimeError("No price results returned")

        result = results[0]
        fields_map = {
            "price.open": result.get("o"),
            "price.high": result.get("h"),
            "price.low": result.get("l"),
            "price.close": result.get("c"),
        }

        fetched: Set[str] = set()
        for field, value in fields_map.items():
            if value is not None and field in requested:
                key = field.split(".", 1)[1]
                data["price"][key] = value
                metadata[field] = {
                    "provider": "polygon.io",
                    "timestamp": payload.get("queryCount"),
                    "endpoint": "/v2/aggs/ticker/{ticker}/prev",
                }
                fetched.add(field)

        return fetched

    def _fetch_ticker_details(
        self,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        payload = self._make_request(f"/v3/reference/tickers/{ticker}")
        result = payload.get("results") or {}

        fields_map = {
            "market_data.market_cap": result.get("market_cap"),
            "market_data.shares_outstanding": result.get("weighted_shares_outstanding"),
        }

        fetched: Set[str] = set()
        for field, value in fields_map.items():
            if value is not None and field in requested:
                key = field.split(".", 1)[1]
                data["market_data"][key] = value
                metadata[field] = {
                    "provider": "polygon.io",
                    "timestamp": result.get("updated"),
                    "endpoint": "/v3/reference/tickers/{ticker}",
                }
                fetched.add(field)

        return fetched

    def _fetch_financials(
        self,
        ticker: str,
        requested: Set[str],
        period: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        timeframe = "annual" if period != "quarterly" else "quarterly"
        payload = self._make_request(
            "/v3/reference/financials",
            params={
                "ticker": ticker,
                "limit": 1,
                "timeframe": timeframe,
            },
        )

        results = payload.get("results") or []
        if not results:
            raise RuntimeError("No financial results returned")

        result = results[0]
        financials = result.get("financials") or {}

        income_statement = financials.get("income_statement") or {}
        balance_sheet = financials.get("balance_sheet") or {}
        cash_flow = financials.get("cash_flow_statement") or {}

        mapping = {
            "financials.revenue": income_statement.get("revenues"),
            "financials.net_income": income_statement.get("net_income_loss"),
            "financials.operating_income": income_statement.get("operating_income_loss"),
            "financials.gross_profit": income_statement.get("gross_profit"),
            "financials.operating_expenses": income_statement.get("operating_expenses"),
            "financials.income_tax_expense": income_statement.get("income_tax_expense_benefit"),
            "financials.interest_expense": income_statement.get("interest_expense"),
            "financials.depreciation_amortization": income_statement.get("depreciation_and_amortization"),
            "financials.ebit": income_statement.get("operating_income_loss"),
            "financials.ebitda": income_statement.get("ebitda"),
            "financials.shareholders_equity": balance_sheet.get("equity"),
            "financials.total_assets": balance_sheet.get("assets"),
            "financials.total_liabilities": balance_sheet.get("liabilities"),
            "financials.cash_and_equivalents": balance_sheet.get("cash_and_cash_equivalents"),
            "financials.current_assets": balance_sheet.get("current_assets"),
            "financials.current_liabilities": balance_sheet.get("current_liabilities"),
            "financials.total_debt": balance_sheet.get("total_debt"),
            "financials.retained_earnings": balance_sheet.get("retained_earnings"),
            "financials.operating_cash_flow": cash_flow.get("net_cash_flow_from_operating_activities"),
            "financials.capital_expenditure": cash_flow.get("capital_expenditure"),
            "cash_flow.dividends_paid": cash_flow.get("dividends_paid"),
        }

        fetched: Set[str] = set()
        for field, value in mapping.items():
            if value is None or field not in requested:
                continue
            section, key = field.split(".", 1)
            data_section = data["cash_flow" if section == "cash_flow" else "financials"]
            data_section[key] = value
            metadata[field] = {
                "provider": "polygon.io",
                "timestamp": result.get("start_date"),
                "endpoint": "/v3/reference/financials",
            }
            fetched.add(field)

        return fetched
