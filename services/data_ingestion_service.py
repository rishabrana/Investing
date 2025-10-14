"""
DataIngestionService - Orchestrates data fetching from multiple providers.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set

from services.fetch_result import FetchResult
from services.data_source_router import DataSourceRouter
from services.normalizer import Normalizer
from storage.json_store import JsonStore, Watchlist, create_raw_snapshot

logger = logging.getLogger(__name__)


class DataIngestionService:
    """
    Orchestrates data fetching and storage.

    This service is stateless and focuses purely on data acquisition.
    It does NOT calculate metrics.

    Workflow:
    1. Load watchlist
    2. For each ticker:
       a. Determine required fields
       b. Route to appropriate API providers via DataSourceRouter
       c. Normalize responses
       d. Store raw data in JsonStore
    3. Track progress for resume capability
    """

    def __init__(
        self,
        json_store: JsonStore,
        data_source_router: DataSourceRouter,
        normalizer: Normalizer,
        period: str = "annual",
        save_history: bool = True,
    ):
        """
        Initialize DataIngestionService.

        Args:
            json_store: Storage backend
            data_source_router: Router for multi-provider data fetching
            normalizer: Normalizes API responses
            period: "annual" or "quarterly"
            save_history: Whether to save historical snapshots
        """
        self.json_store = json_store
        self.router = data_source_router
        self.normalizer = normalizer
        self.period = period
        self.save_history = save_history

    def _get_required_fields(self) -> Set[str]:
        """
        Determine which fields need to be fetched.

        For now, we fetch a standard set of fields.
        Future enhancement: derive from metrics configuration.

        Returns:
            Set of field identifiers (e.g., 'price.close', 'financials.revenue')
        """
        return {
            # Price data
            "price.close",
            "price.open",
            "price.high",
            "price.low",
            # Market data
            "market_data.market_cap",
            "market_data.shares_outstanding",
            # Balance sheet
            "financials.shareholders_equity",
            "financials.total_liabilities",
            "financials.cash_and_equivalents",
            "financials.total_debt",
            "financials.total_assets",
            "financials.current_assets",
            "financials.current_liabilities",
            "financials.retained_earnings",
            # Income statement
            "financials.revenue",
            "financials.net_income",
            "financials.operating_income",
            "financials.gross_profit",
            "financials.operating_expenses",
            "financials.income_tax_expense",
            "financials.interest_expense",
            "financials.depreciation_amortization",
            "financials.ebit",
            "financials.ebitda",
            # Cash flow
            "financials.operating_cash_flow",
            "financials.capital_expenditure",
            "cash_flow.dividends_paid",
        }

    def refresh_ticker(
        self,
        ticker: str,
        required_fields: Optional[Set[str]] = None,
    ) -> FetchResult:
        """
        Fetch and store data for a single ticker.

        Args:
            ticker: Stock ticker symbol
            required_fields: Specific fields to fetch. If None, uses standard set.

        Returns:
            FetchResult with success status and details
        """
        logger.info("Refreshing data for %s", ticker)

        ticker = ticker.upper()
        fields = required_fields or self._get_required_fields()

        try:
            fetch_response = self.router.fetch_fields(
                ticker=ticker,
                fields=fields,
                period=self.period,
            )

            normalized = self.normalizer.normalize(
                ticker=ticker,
                raw_data=fetch_response.data,
                source_metadata=fetch_response.source_metadata,
            )

            snapshot = create_raw_snapshot(
                ticker=ticker,
                as_of=normalized.get("as_of", datetime.utcnow().strftime("%Y-%m-%d")),
                price=normalized.get("price"),
                financials=normalized.get("financials"),
                market_data=normalized.get("market_data"),
                cash_flow=normalized.get("cash_flow"),
                assumptions=normalized.get("assumptions"),
                financials_history=normalized.get("financials_history"),
                market_data_history=normalized.get("market_data_history"),
                cash_flow_history=normalized.get("cash_flow_history"),
                metrics_history=normalized.get("metrics_history"),
                projections=normalized.get("projections"),
                source_metadata=normalized.get("source_metadata"),
                raw_payloads=fetch_response.raw_payloads,
            )

            self.json_store.write_raw_snapshot(
                snapshot=snapshot,
                save_history=self.save_history,
            )

            result = FetchResult(
                ticker=ticker,
                success=True,
                snapshot=snapshot,
                warnings=fetch_response.warnings,
                fields_fetched=fetch_response.fields_fetched,
                fields_missing=fetch_response.fields_missing,
                providers_used=fetch_response.providers_used,
            )

            logger.info(
                "Successfully fetched %s: %d fields from %d providers",
                ticker,
                len(result.fields_fetched),
                len(result.providers_used),
            )

            return result

        except Exception as exc:  # pragma: no cover - logged unexpected failures
            logger.error("Failed to fetch %s: %s", ticker, exc, exc_info=True)
            return FetchResult(
                ticker=ticker,
                success=False,
                errors=[str(exc)],
            )

    def refresh_watchlist(
        self,
        watchlist: Watchlist,
        resume: bool = False,
        max_tickers: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Fetch and store data for all tickers in watchlist.

        Args:
            watchlist: Watchlist with tickers to fetch
            resume: If True, skip tickers already fetched in this run
            max_tickers: Optional limit on number of tickers to process

        Returns:
            Summary report with results for each ticker
        """
        logger.info(
            "Refreshing watchlist with %d tickers (resume=%s)",
            len(watchlist.tickers),
            resume,
        )

        completed = set()
        if resume:
            state = self.json_store.load_fetch_state()
            if state:
                completed = set(state.get("completed", []))
                logger.info("Resuming: %d already completed", len(completed))

        results = []
        required_fields = self._get_required_fields()

        for index, entry in enumerate(watchlist.tickers):
            if max_tickers and index >= max_tickers:
                logger.info("Reached max_tickers limit: %d", max_tickers)
                break

            if resume and entry.symbol in completed:
                logger.info("Skipping %s (already completed)", entry.symbol)
                continue

            result = self.refresh_ticker(
                ticker=entry.symbol,
                required_fields=required_fields,
            )
            results.append(result)

            if result.success:
                completed.add(entry.symbol)
                self.json_store.save_fetch_state(
                    {
                        "started_at": datetime.utcnow().isoformat(),
                        "completed": list(completed),
                        "total": len(watchlist.tickers),
                    }
                )

        if len(completed) >= len(watchlist.tickers):
            self.json_store.clear_fetch_state()

        return self._generate_summary(results, watchlist)

    def _generate_summary(
        self,
        results: list[FetchResult],
        watchlist: Watchlist,
    ) -> Dict[str, Any]:
        """Generate summary report from fetch results."""
        successful = [result for result in results if result.success]
        failed = [result for result in results if not result.success]

        total_providers_used: Dict[str, int] = {}
        for result in successful:
            for provider, count in result.providers_used.items():
                total_providers_used[provider] = (
                    total_providers_used.get(provider, 0) + count
                )

        all_fields_fetched: Set[str] = set()
        all_fields_missing: Set[str] = set()
        for result in successful:
            all_fields_fetched.update(result.fields_fetched)
            all_fields_missing.update(result.fields_missing)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "watchlist_size": len(watchlist.tickers),
            "processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "providers_used": total_providers_used,
            "unique_fields_fetched": len(all_fields_fetched),
            "unique_fields_missing": len(all_fields_missing),
            "results": [result.to_dict() for result in results],
            "failed_tickers": [result.ticker for result in failed],
        }


__all__ = ["DataIngestionService"]
