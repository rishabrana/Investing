"""Yahoo Finance API client using yfinance library."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Set, Tuple

try:
    import yfinance as yf
except ImportError:
    yf = None


logger = logging.getLogger(__name__)


class YahooFinanceClient:
    """Yahoo Finance client using yfinance library."""

    def __init__(self):
        """Initialize Yahoo Finance client."""
        if yf is None:
            raise ImportError(
                "yfinance library is required. Install with: pip install yfinance"
            )

    def fetch_fields(
        self,
        ticker: str,
        fields: Iterable[str],
        period: str = "annual",
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str], list[str]]:
        """
        Fetch the requested fields from Yahoo Finance.

        Args:
            ticker: Stock ticker symbol
            fields: Field IDs to fetch
            period: "annual" or "quarterly" (currently only annual supported)

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

        try:
            stock = yf.Ticker(ticker)

            # Fetch market data (P/E ratios, etc.) if needed
            need_market_data = any(
                f.startswith("market_data.")
                for f in requested
            )

            if need_market_data:
                fetched |= self._fetch_market_data(
                    stock, ticker, requested, data, source_metadata
                )

            # Fetch financials if needed
            need_financials = any(
                f.startswith("financials.") or f.startswith("cash_flow.")
                for f in requested
            )

            if need_financials:
                fetched |= self._fetch_financials(
                    stock, ticker, requested, data, source_metadata
                )

        except Exception as exc:
            msg = f"Yahoo Finance fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        return data, source_metadata, fetched, warnings

    def _fetch_market_data(
        self,
        stock: Any,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        """Fetch market data including P/E ratios."""
        fetched: Set[str] = set()

        try:
            info = stock.info

            # P/E ratio mappings
            pe_mapping = {
                "market_data.trailing_pe": "trailingPE",
                "market_data.forward_pe": "forwardPE",
            }

            for field, info_key in pe_mapping.items():
                if field in requested:
                    value = info.get(info_key)
                    if value is not None and value != "None":
                        try:
                            section, key = field.split(".", 1)
                            data["market_data"][key] = float(value)
                            metadata[field] = {
                                "provider": "yahoo_finance",
                                "timestamp": None,  # Info data doesn't have timestamp
                                "endpoint": "info",
                            }
                            fetched.add(field)
                        except (ValueError, TypeError):
                            logger.warning(f"Could not convert {field} value: {value}")

        except Exception as exc:
            logger.warning(f"Error fetching Yahoo Finance market data: {exc}")

        return fetched

    def _fetch_financials(
        self,
        stock: Any,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        """Fetch financial statement data."""
        fetched: Set[str] = set()

        try:
            # Get annual financials
            income_stmt = stock.income_stmt
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cash_flow

            # Income statement mappings
            income_mapping = {
                "financials.interest_expense": "Interest Expense",
                "financials.depreciation_amortization": "Reconciled Depreciation",
                "financials.ebitda": "EBITDA",
            }

            if income_stmt is not None and not income_stmt.empty:
                # Get most recent column (usually first column)
                latest = income_stmt.iloc[:, 0]
                for field, yf_field in income_mapping.items():
                    if field in requested and yf_field in latest.index:
                        value = latest[yf_field]
                        if value is not None and not (
                            hasattr(value, "isna") and value.isna()
                        ):
                            section, key = field.split(".", 1)
                            data["financials"][key] = float(value)
                            metadata[field] = {
                                "provider": "yahoo_finance",
                                "timestamp": income_stmt.columns[0].strftime(
                                    "%Y-%m-%d"
                                )
                                if hasattr(income_stmt.columns[0], "strftime")
                                else str(income_stmt.columns[0]),
                                "endpoint": "income_stmt",
                            }
                            fetched.add(field)

            # Balance sheet mappings
            balance_mapping = {
                "financials.retained_earnings": "Retained Earnings",
                "financials.cash_and_equivalents": "Cash And Cash Equivalents",
            }

            if balance_sheet is not None and not balance_sheet.empty:
                latest = balance_sheet.iloc[:, 0]
                for field, yf_field in balance_mapping.items():
                    if field in requested and yf_field in latest.index:
                        value = latest[yf_field]
                        if value is not None and not (
                            hasattr(value, "isna") and value.isna()
                        ):
                            section, key = field.split(".", 1)
                            data["financials"][key] = float(value)
                            metadata[field] = {
                                "provider": "yahoo_finance",
                                "timestamp": balance_sheet.columns[0].strftime(
                                    "%Y-%m-%d"
                                )
                                if hasattr(balance_sheet.columns[0], "strftime")
                                else str(balance_sheet.columns[0]),
                                "endpoint": "balance_sheet",
                            }
                            fetched.add(field)

            # Cash flow mappings
            cashflow_mapping = {
                "financials.capital_expenditure": "Capital Expenditure",
                "cash_flow.dividends_paid": [
                    "Cash Dividends Paid",
                    "Common Stock Dividend Paid",
                ],
            }

            if cash_flow is not None and not cash_flow.empty:
                latest = cash_flow.iloc[:, 0]
                for field, yf_fields in cashflow_mapping.items():
                    if field not in requested:
                        continue

                    # Handle multiple possible field names
                    if isinstance(yf_fields, list):
                        yf_field = None
                        for possible_field in yf_fields:
                            if possible_field in latest.index:
                                yf_field = possible_field
                                break
                    else:
                        yf_field = yf_fields if yf_fields in latest.index else None

                    if yf_field:
                        value = latest[yf_field]
                        if value is not None and not (
                            hasattr(value, "isna") and value.isna()
                        ):
                            section, key = field.split(".", 1)
                            data_section = (
                                data["cash_flow"]
                                if section == "cash_flow"
                                else data["financials"]
                            )
                            data_section[key] = float(value)
                            metadata[field] = {
                                "provider": "yahoo_finance",
                                "timestamp": cash_flow.columns[0].strftime("%Y-%m-%d")
                                if hasattr(cash_flow.columns[0], "strftime")
                                else str(cash_flow.columns[0]),
                                "endpoint": "cash_flow",
                            }
                            fetched.add(field)

        except Exception as exc:
            logger.warning(f"Error fetching Yahoo Finance financials: {exc}")

        return fetched
