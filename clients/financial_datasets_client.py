"""financialdatasets.ai API client wrapped for DataSourceRouter usage."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Set, Tuple

import requests


logger = logging.getLogger(__name__)


class FinancialDatasetsClient:
    """Lightweight financialdatasets.ai REST client."""

    BASE_URL = "https://api.financialdatasets.ai"

    def __init__(self, api_key: str, session: requests.Session | None = None):
        if not api_key:
            raise ValueError("financialdatasets.ai API key is required")
        self.api_key = api_key
        self.session = session or requests.Session()

    # -------- public API --------

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

        # Block A: Price snapshot (close price only)
        try:
            if "price.close" in requested:
                fetched |= self._fetch_price(ticker, requested, data, source_metadata)
        except Exception as exc:
            msg = f"FinancialDatasets price fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        # Block B: Financial statements (income, balance, cash flow + history)
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
        except Exception as exc:
            msg = f"FinancialDatasets financials fetch failed for {ticker}: {exc}"
            logger.warning(msg)
            warnings.append(msg)

        return data, source_metadata, fetched, warnings

    # -------- internal helpers --------

    def _make_request(self, path: str, params: Dict[str, Any] | None = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        headers = {"X-API-KEY": self.api_key}
        response = self.session.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def _fetch_price(
        self,
        ticker: str,
        requested: Set[str],
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Set[str]:
        """Fetch close price from /prices/snapshot.

        The snapshot response only contains close price (field: 'price'),
        volume, and day change. open/high/low/market_cap/shares_outstanding
        are NOT available here and must come from polygon.io.
        """
        payload = self._make_request("/prices/snapshot", params={"ticker": ticker})
        snapshot = payload.get("snapshot") or {}

        close = snapshot.get("price")
        if close is None:
            raise RuntimeError("No price in snapshot response")

        fetched: Set[str] = set()
        if "price.close" in requested:
            data["price"]["close"] = close
            metadata["price.close"] = {
                "provider": "financial_datasets",
                "timestamp": snapshot.get("time", ""),
                "endpoint": "/prices/snapshot",
            }
            fetched.add("price.close")

        return fetched

    def _fetch_financials(
        self,
        ticker: str,
        requested: Set[str],
        period: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        limit: int = 10,
    ) -> Set[str]:
        """Fetch income statement, balance sheet, and cash flow statement.

        Makes three API calls, extracts current-period fields, derives ebitda,
        and builds financials_history / cash_flow_history arrays.
        """
        fd_period = "annual" if period != "quarterly" else "quarterly"

        # Fetch all three statements
        income_payload = self._make_request(
            "/financials/income-statements",
            params={"ticker": ticker, "period": fd_period, "limit": limit},
        )
        balance_payload = self._make_request(
            "/financials/balance-sheets",
            params={"ticker": ticker, "period": fd_period, "limit": limit},
        )
        cashflow_payload = self._make_request(
            "/financials/cash-flow-statements",
            params={"ticker": ticker, "period": fd_period, "limit": limit},
        )

        income_list = income_payload.get("income_statements") or []
        balance_list = balance_payload.get("balance_sheets") or []
        cashflow_list = cashflow_payload.get("cash_flow_statements") or []

        if not income_list and not balance_list and not cashflow_list:
            raise RuntimeError("No financial data returned from financialdatasets.ai")

        # Most recent period is index 0
        income = income_list[0] if income_list else {}
        balance = balance_list[0] if balance_list else {}
        cashflow = cashflow_list[0] if cashflow_list else {}

        # Pull D&A from cash flow (not present in income statement)
        da = cashflow.get("depreciation_and_amortization")

        # Derive EBITDA = EBIT + D&A
        ebit_val = income.get("ebit")
        ebitda_val = None
        if ebit_val is not None and da is not None:
            ebitda_val = ebit_val + da

        # Field mapping: (field_id, value, source_endpoint)
        # Income statement fields
        income_fields = {
            "financials.revenue": income.get("revenue"),
            "financials.net_income": income.get("net_income"),
            "financials.operating_income": income.get("operating_income"),
            "financials.gross_profit": income.get("gross_profit"),
            "financials.operating_expenses": income.get("operating_expense"),  # singular in API
            "financials.income_tax_expense": income.get("income_tax_expense"),
            "financials.interest_expense": income.get("interest_expense"),
            "financials.ebit": ebit_val,
        }

        # Balance sheet fields
        balance_fields = {
            "financials.shareholders_equity": balance.get("shareholders_equity"),
            "financials.total_liabilities": balance.get("total_liabilities"),
            "financials.cash_and_equivalents": balance.get("cash_and_equivalents"),
            "financials.total_debt": balance.get("total_debt"),
            "financials.total_assets": balance.get("total_assets"),
            "financials.current_assets": balance.get("current_assets"),
            "financials.current_liabilities": balance.get("current_liabilities"),
            "financials.retained_earnings": balance.get("retained_earnings"),
        }

        # Cash flow fields (capital_expenditure and dividends are negative in API)
        cashflow_fields = {
            "financials.operating_cash_flow": cashflow.get("net_cash_flow_from_operations"),
            "financials.capital_expenditure": cashflow.get("capital_expenditure"),
            "financials.depreciation_amortization": da,
            "financials.ebitda": ebitda_val,
            "cash_flow.dividends_paid": cashflow.get("dividends_and_other_cash_distributions"),
        }

        # Populate data dict and track fetched fields
        fetched: Set[str] = set()

        for field_id, value in income_fields.items():
            if value is None or field_id not in requested:
                continue
            data["financials"][field_id.split(".", 1)[1]] = value
            metadata[field_id] = {
                "provider": "financial_datasets",
                "timestamp": income.get("report_period", ""),
                "endpoint": "/financials/income-statements",
            }
            fetched.add(field_id)

        for field_id, value in balance_fields.items():
            if value is None or field_id not in requested:
                continue
            data["financials"][field_id.split(".", 1)[1]] = value
            metadata[field_id] = {
                "provider": "financial_datasets",
                "timestamp": balance.get("report_period", ""),
                "endpoint": "/financials/balance-sheets",
            }
            fetched.add(field_id)

        for field_id, value in cashflow_fields.items():
            if value is None or field_id not in requested:
                continue
            section, key = field_id.split(".", 1)
            target = data["cash_flow"] if section == "cash_flow" else data["financials"]
            target[key] = value
            metadata[field_id] = {
                "provider": "financial_datasets",
                "timestamp": cashflow.get("report_period", ""),
                "endpoint": "/financials/cash-flow-statements",
            }
            fetched.add(field_id)

        # ---- Build history arrays ----
        # Zip the three lists by index; use min length to avoid index errors
        max_periods = min(len(income_list), len(balance_list), len(cashflow_list))
        financials_history = []
        cash_flow_history = []

        for i in range(max_periods):
            inc = income_list[i]
            bal = balance_list[i]
            cf = cashflow_list[i]

            period_label = inc.get("report_period", "")

            # Derive per-period D&A and EBITDA
            hist_da = cf.get("depreciation_and_amortization")
            hist_ebit = inc.get("ebit")
            hist_ebitda = None
            if hist_ebit is not None and hist_da is not None:
                hist_ebitda = hist_ebit + hist_da

            hist_entry: Dict[str, Any] = {
                "period": period_label,
                "revenue": inc.get("revenue"),
                "net_income": inc.get("net_income"),
                "operating_income": inc.get("operating_income"),
                "gross_profit": inc.get("gross_profit"),
                "ebit": hist_ebit,
                "ebitda": hist_ebitda,
                "shareholders_equity": bal.get("shareholders_equity"),
                "total_assets": bal.get("total_assets"),
                "total_liabilities": bal.get("total_liabilities"),
                "current_liabilities": bal.get("current_liabilities"),
                "current_assets": bal.get("current_assets"),
                "retained_earnings": bal.get("retained_earnings"),
                "total_debt": bal.get("total_debt"),
                "cash_and_equivalents": bal.get("cash_and_equivalents"),
                "operating_cash_flow": cf.get("net_cash_flow_from_operations"),
                "capital_expenditure": cf.get("capital_expenditure"),
                "shares_outstanding": bal.get("outstanding_shares"),
            }

            # Derived margins
            rev = hist_entry["revenue"]
            if rev and hist_entry["gross_profit"]:
                hist_entry["gross_margin"] = hist_entry["gross_profit"] / rev
            if rev and hist_entry["operating_income"]:
                hist_entry["operating_margin"] = hist_entry["operating_income"] / rev

            financials_history.append(hist_entry)

            # Cash flow history — use pre-computed free_cash_flow from API
            cf_hist: Dict[str, Any] = {
                "period": period_label,
                "operating_cash_flow": cf.get("net_cash_flow_from_operations"),
                "capital_expenditure": cf.get("capital_expenditure"),
                "dividends_paid": cf.get("dividends_and_other_cash_distributions"),
                "free_cash_flow": cf.get("free_cash_flow"),
            }
            cash_flow_history.append(cf_hist)

        data["financials_history"] = financials_history
        data["cash_flow_history"] = cash_flow_history

        return fetched
