"""
MetricsService - Orchestrates metric calculation from raw data.

This service:
1. Reads raw financial data from JsonStore
2. Calculates all configured metrics using MetricCalculator classes
3. Stores computed metrics back to JsonStore

Maintains strict separation between raw data and computed metrics.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from services.metric_calculator import (
    MetricCalculator,
    MetricResult,
    get_all_calculators,
    get_calculator_by_id
)
from storage.json_store import (
    JsonStore,
    MetricsSnapshot,
    RawSnapshot,
    create_metrics_snapshot
)

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Service for calculating investment metrics from raw data.

    Workflow:
    1. Load raw data snapshot for a ticker
    2. Calculate all configured metrics
    3. Organize results by category
    4. Store metrics snapshot
    """

    def __init__(
        self,
        json_store: JsonStore,
        metric_catalog_path: str = "config/metric_catalog.yaml"
    ):
        """
        Initialize MetricsService.

        Args:
            json_store: Storage backend
            metric_catalog_path: Path to metric catalog YAML
        """
        self.json_store = json_store
        self.metric_catalog_path = Path(metric_catalog_path)

        # Load metric catalog
        self.metric_catalog = self._load_metric_catalog()

        # Get all available calculators
        self.calculators = {
            calc.metric_id: calc
            for calc in get_all_calculators()
        }

        # Define category mapping
        self.category_mapping = self._build_category_mapping()

    def _load_metric_catalog(self) -> Dict[str, Any]:
        """Load metric catalog from YAML."""
        if not self.metric_catalog_path.exists():
            logger.warning(f"Metric catalog not found at {self.metric_catalog_path}")
            return {'metrics': {}}

        with open(self.metric_catalog_path, 'r') as f:
            return yaml.safe_load(f)

    def _build_category_mapping(self) -> Dict[str, str]:
        """
        Build mapping of metric_id to category.

        Categories:
        - valuation
        - profitability
        - cash_generation
        - financial_strength
        - capital_allocation
        - moat
        """
        return {
            # Valuation
            'price_to_earnings': 'valuation',
            'forward_pe': 'valuation',
            'price_to_book': 'valuation',
            'ev_to_ebitda': 'valuation',
            'peg_ratio': 'valuation',
            'margin_of_safety': 'valuation',

            # Profitability
            'return_on_invested_capital': 'profitability',
            'return_on_equity': 'profitability',
            'operating_and_net_margin': 'profitability',
            'ten_year_average_roce': 'profitability',
            'earnings_stability': 'profitability',

            # Cash Generation
            'free_cash_flow': 'cash_generation',
            'owner_earnings': 'cash_generation',
            'capital_expenditure_ratio': 'cash_generation',

            # Financial Strength
            'debt_to_equity_and_interest_coverage': 'financial_strength',
            'current_ratio': 'financial_strength',

            # Capital Allocation
            'dividend_yield_and_payout_ratio': 'capital_allocation',
            'dividend_history': 'capital_allocation',
            'return_on_retained_earnings': 'capital_allocation',
            'wacc_vs_roic_spread': 'capital_allocation',

            # Moat
            'economic_moat_score': 'moat',
            'consistency_score': 'moat',
            'piotroski_fscore': 'moat',

            # Growth
            'eps_growth': 'profitability',
            'book_value_per_share_growth': 'profitability',
        }

    def calculate_metrics(
        self,
        ticker: str,
        profile: str = "buffett_core",
        save_history: bool = True
    ) -> MetricsSnapshot:
        """
        Calculate all metrics for a ticker.

        Args:
            ticker: Stock ticker symbol
            profile: Metrics profile to use
            save_history: Whether to save to history

        Returns:
            MetricsSnapshot with calculated metrics
        """
        logger.info(f"Calculating metrics for {ticker} (profile: {profile})")

        # Load raw data
        raw_snapshot = self.json_store.read_raw_snapshot(ticker)
        if not raw_snapshot:
            raise ValueError(f"No raw data found for ticker: {ticker}")

        # Convert snapshot to dict for calculations
        raw_data = {
            'ticker': raw_snapshot.ticker,
            'as_of': raw_snapshot.as_of,
            'price': raw_snapshot.price or {},
            'financials': raw_snapshot.financials or {},
            'market_data': raw_snapshot.market_data or {},
            'cash_flow': raw_snapshot.cash_flow or {},
            'assumptions': raw_snapshot.assumptions or {},
            'financials_history': raw_snapshot.financials_history or [],
            'market_data_history': raw_snapshot.market_data_history or [],
            'cash_flow_history': raw_snapshot.cash_flow_history or [],
            'metrics_history': raw_snapshot.metrics_history or [],
            'projections': raw_snapshot.projections or {},
        }

        # Calculate all metrics
        results = self._calculate_all_metrics(raw_data)

        # Organize by category
        categorized = self._categorize_results(results)

        # Collect metadata
        metrics_included = [r.metric_id for r in results if r.success]
        notes = []
        warnings = []

        for result in results:
            if not result.success:
                warnings.append(f"{result.metric_id}: {result.error}")
            if result.warnings:
                warnings.extend(result.warnings)

        # Create metrics snapshot
        snapshot = create_metrics_snapshot(
            ticker=ticker,
            as_of=raw_snapshot.as_of,
            profile_used=profile,
            valuation=categorized.get('valuation'),
            profitability=categorized.get('profitability'),
            cash_generation=categorized.get('cash_generation'),
            financial_strength=categorized.get('financial_strength'),
            capital_allocation=categorized.get('capital_allocation'),
            moat=categorized.get('moat'),
            metrics_included=metrics_included,
            notes=notes,
            warnings=warnings if warnings else None
        )

        # Save to store
        self.json_store.write_metrics_snapshot(
            snapshot=snapshot,
            save_history=save_history
        )

        logger.info(
            f"Calculated {len(metrics_included)} metrics for {ticker} "
            f"({len(warnings)} warnings)"
        )

        return snapshot

    def _calculate_all_metrics(
        self,
        raw_data: Dict[str, Any]
    ) -> List[MetricResult]:
        """
        Calculate all available metrics.

        Args:
            raw_data: Raw financial data

        Returns:
            List of MetricResult objects
        """
        results = []

        for metric_id, calculator in self.calculators.items():
            try:
                result = calculator.calculate(raw_data)
                results.append(result)

                if result.success:
                    logger.debug(f"✓ {metric_id}: {result.value}")
                else:
                    logger.debug(f"✗ {metric_id}: {result.error}")

            except Exception as exc:
                logger.error(f"Error calculating {metric_id}: {exc}", exc_info=True)
                results.append(MetricResult(
                    metric_id=metric_id,
                    value=None,
                    success=False,
                    error=str(exc)
                ))

        return results

    def _categorize_results(
        self,
        results: List[MetricResult]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Organize metric results by category.

        Args:
            results: List of metric results

        Returns:
            Dict mapping category to metric values
        """
        categorized: Dict[str, Dict[str, Any]] = {
            'valuation': {},
            'profitability': {},
            'cash_generation': {},
            'financial_strength': {},
            'capital_allocation': {},
            'moat': {},
        }

        for result in results:
            if not result.success or result.value is None:
                continue

            category = self.category_mapping.get(result.metric_id, 'profitability')
            categorized[category][result.metric_id] = result.value

        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}

        return categorized

    def calculate_for_watchlist(
        self,
        watchlist_name: str = "default",
        max_tickers: Optional[int] = None,
        save_history: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate metrics for all tickers in a watchlist.

        Args:
            watchlist_name: Name of watchlist to process
            max_tickers: Optional limit on tickers to process
            save_history: Whether to save to history

        Returns:
            Summary report with results
        """
        logger.info(f"Calculating metrics for watchlist: {watchlist_name}")

        # Load watchlist
        watchlist = self.json_store.load_watchlist(watchlist_name)
        if not watchlist:
            raise ValueError(f"Watchlist not found: {watchlist_name}")

        results = []
        successful = 0
        failed = 0

        for index, entry in enumerate(watchlist.tickers):
            if max_tickers and index >= max_tickers:
                logger.info(f"Reached max_tickers limit: {max_tickers}")
                break

            ticker = entry.symbol
            profile = entry.metrics_profile or watchlist.default_metrics_profile

            try:
                snapshot = self.calculate_metrics(
                    ticker=ticker,
                    profile=profile,
                    save_history=save_history
                )
                successful += 1
                results.append({
                    'ticker': ticker,
                    'success': True,
                    'metrics_calculated': len(snapshot.metrics_included or []),
                    'warnings': len(snapshot.warnings or [])
                })
            except Exception as exc:
                logger.error(f"Failed to calculate metrics for {ticker}: {exc}")
                failed += 1
                results.append({
                    'ticker': ticker,
                    'success': False,
                    'error': str(exc)
                })

        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'watchlist': watchlist_name,
            'watchlist_size': len(watchlist.tickers),
            'processed': len(results),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(results) if results else 0,
            'results': results
        }

        return summary

    def get_metrics_summary(
        self,
        ticker: str,
        timestamp: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a summary of calculated metrics for a ticker.

        Args:
            ticker: Stock ticker symbol
            timestamp: Optional specific timestamp

        Returns:
            Dict with metrics summary or None
        """
        snapshot = self.json_store.read_metrics_snapshot(ticker, timestamp)
        if not snapshot:
            return None

        # Flatten metrics for easy display
        all_metrics = {}

        for category in ['valuation', 'profitability', 'cash_generation',
                        'financial_strength', 'capital_allocation', 'moat']:
            category_data = getattr(snapshot, category, None)
            if category_data:
                for key, value in category_data.items():
                    all_metrics[key] = value

        return {
            'ticker': snapshot.ticker,
            'as_of': snapshot.as_of,
            'calculated_at': snapshot.calculated_at,
            'profile': snapshot.profile_used,
            'metrics_count': len(snapshot.metrics_included or []),
            'metrics': all_metrics,
            'warnings': snapshot.warnings
        }


__all__ = ['MetricsService']
