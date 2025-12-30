"""
Metric Calculator - Base classes and utilities for calculating investment metrics.

This module provides the infrastructure for calculating various investment metrics
from raw financial data. Each metric is implemented as a separate calculator class.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class MetricResult:
    """Result of a metric calculation."""
    metric_id: str
    value: Any
    success: bool
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricCalculator(ABC):
    """
    Base class for all metric calculators.

    Each calculator implements the logic to compute one specific metric
    from raw financial data.
    """

    def __init__(self, metric_id: str, display_name: str):
        """
        Initialize metric calculator.

        Args:
            metric_id: Unique identifier for this metric
            display_name: Human-readable name
        """
        self.metric_id = metric_id
        self.display_name = display_name

    @abstractmethod
    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        """
        Calculate the metric from raw data.

        Args:
            raw_data: Raw financial data snapshot

        Returns:
            MetricResult with calculated value
        """
        pass

    def safe_divide(self, numerator: float, denominator: float, default: Any = None) -> Optional[float]:
        """
        Safely divide two numbers, handling zero division.

        Args:
            numerator: Numerator value
            denominator: Denominator value
            default: Value to return if division fails

        Returns:
            Result of division or default
        """
        if denominator == 0 or denominator is None:
            return default
        return numerator / denominator

    def get_value(self, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Safely get nested value from data dictionary using dot notation.

        Args:
            data: Data dictionary
            path: Dot-separated path (e.g., 'financials.revenue')
            default: Default value if path not found

        Returns:
            Value at path or default
        """
        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def check_required_fields(
        self,
        data: Dict[str, Any],
        required: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Check if all required fields are present in data.

        Args:
            data: Data dictionary
            required: List of required field paths

        Returns:
            Tuple of (all_present, missing_fields)
        """
        missing = []
        for field in required:
            value = self.get_value(data, field)
            if value is None:
                missing.append(field)

        return len(missing) == 0, missing


# ===== PROFITABILITY METRICS =====

class FreeCashFlowCalculator(MetricCalculator):
    """Calculate Free Cash Flow."""

    def __init__(self):
        super().__init__('free_cash_flow', 'Free Cash Flow')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        operating_cf = self.get_value(raw_data, 'financials.operating_cash_flow')
        capex = self.get_value(raw_data, 'financials.capital_expenditure')

        if operating_cf is None or capex is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing required fields: operating_cash_flow or capital_expenditure'
            )

        # capex is usually negative, so we add it
        fcf = operating_cf + capex

        return MetricResult(
            metric_id=self.metric_id,
            value=fcf,
            success=True,
            metadata={
                'operating_cash_flow': operating_cf,
                'capital_expenditure': capex
            }
        )


class ROICCalculator(MetricCalculator):
    """Calculate Return on Invested Capital."""

    def __init__(self):
        super().__init__('return_on_invested_capital', 'Return on Invested Capital (ROIC)')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        ebit = self.get_value(raw_data, 'financials.ebit')
        income_tax = self.get_value(raw_data, 'financials.income_tax_expense')
        pre_tax_income = self.get_value(raw_data, 'financials.pre_tax_income')
        total_debt = self.get_value(raw_data, 'financials.total_debt')
        equity = self.get_value(raw_data, 'financials.shareholders_equity')
        cash = self.get_value(raw_data, 'financials.cash_and_equivalents')

        required_fields = ['ebit', 'total_debt', 'shareholders_equity']
        missing = []
        if ebit is None:
            missing.append('ebit')
        if total_debt is None:
            missing.append('total_debt')
        if equity is None:
            missing.append('shareholders_equity')

        if missing:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error=f'Missing required fields: {", ".join(missing)}'
            )

        # Calculate effective tax rate
        if pre_tax_income and pre_tax_income != 0 and income_tax:
            tax_rate = income_tax / pre_tax_income
        else:
            tax_rate = 0.21  # Default US corporate tax rate

        # Calculate NOPAT
        nopat = ebit * (1 - tax_rate)

        # Calculate invested capital
        invested_capital = total_debt + equity - (cash or 0)

        # Calculate ROIC
        roic = self.safe_divide(nopat, invested_capital)

        if roic is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Invested capital is zero'
            )

        return MetricResult(
            metric_id=self.metric_id,
            value=roic,
            success=True,
            metadata={
                'nopat': nopat,
                'invested_capital': invested_capital,
                'tax_rate': tax_rate
            }
        )


class ROECalculator(MetricCalculator):
    """Calculate Return on Equity."""

    def __init__(self):
        super().__init__('return_on_equity', 'Return on Equity (ROE)')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        net_income = self.get_value(raw_data, 'financials.net_income')
        equity = self.get_value(raw_data, 'financials.shareholders_equity')

        if net_income is None or equity is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing required fields: net_income or shareholders_equity'
            )

        roe = self.safe_divide(net_income, equity)

        if roe is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Shareholders equity is zero'
            )

        return MetricResult(
            metric_id=self.metric_id,
            value=roe,
            success=True,
            metadata={
                'net_income': net_income,
                'shareholders_equity': equity
            }
        )


class OperatingMarginsCalculator(MetricCalculator):
    """Calculate Operating and Net Margins."""

    def __init__(self):
        super().__init__('operating_and_net_margin', 'Operating Margin & Net Margin')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        operating_income = self.get_value(raw_data, 'financials.operating_income')
        net_income = self.get_value(raw_data, 'financials.net_income')
        revenue = self.get_value(raw_data, 'financials.revenue')

        if revenue is None or revenue == 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing or zero revenue'
            )

        operating_margin = self.safe_divide(operating_income, revenue) if operating_income else None
        net_margin = self.safe_divide(net_income, revenue) if net_income else None

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'operating_margin': operating_margin,
                'net_margin': net_margin
            },
            success=True,
            metadata={
                'operating_income': operating_income,
                'net_income': net_income,
                'revenue': revenue
            }
        )


class OwnerEarningsCalculator(MetricCalculator):
    """Calculate Owner Earnings (Buffett's metric)."""

    def __init__(self):
        super().__init__('owner_earnings', 'Owner Earnings')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        net_income = self.get_value(raw_data, 'financials.net_income')
        depreciation = self.get_value(raw_data, 'financials.depreciation_amortization')
        capex = self.get_value(raw_data, 'financials.capital_expenditure')

        if net_income is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing required field: net_income'
            )

        # Owner Earnings = Net Income + D&A - CapEx
        owner_earnings = net_income
        if depreciation:
            owner_earnings += depreciation
        if capex:
            owner_earnings += capex  # capex is negative

        return MetricResult(
            metric_id=self.metric_id,
            value=owner_earnings,
            success=True,
            metadata={
                'net_income': net_income,
                'depreciation_amortization': depreciation,
                'capital_expenditure': capex
            }
        )


# ===== FINANCIAL STRENGTH METRICS =====

class DebtToEquityCalculator(MetricCalculator):
    """Calculate Debt-to-Equity and Interest Coverage."""

    def __init__(self):
        super().__init__('debt_to_equity_and_interest_coverage', 'Debt-to-Equity & Interest Coverage')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        total_liabilities = self.get_value(raw_data, 'financials.total_liabilities')
        equity = self.get_value(raw_data, 'financials.shareholders_equity')
        ebit = self.get_value(raw_data, 'financials.ebit')
        interest_expense = self.get_value(raw_data, 'financials.interest_expense')

        if equity is None or equity == 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing or zero shareholders_equity'
            )

        debt_to_equity = self.safe_divide(total_liabilities, equity)

        # Interest coverage
        interest_coverage = None
        if ebit and interest_expense and interest_expense != 0:
            interest_coverage = ebit / interest_expense

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'debt_to_equity': debt_to_equity,
                'interest_coverage': interest_coverage
            },
            success=True,
            metadata={
                'total_liabilities': total_liabilities,
                'shareholders_equity': equity,
                'ebit': ebit,
                'interest_expense': interest_expense
            }
        )


class CapexRatioCalculator(MetricCalculator):
    """Calculate Capital Expenditure Ratio."""

    def __init__(self):
        super().__init__('capital_expenditure_ratio', 'Capital Expenditure Ratio')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        capex = self.get_value(raw_data, 'financials.capital_expenditure')
        operating_cf = self.get_value(raw_data, 'financials.operating_cash_flow')

        if capex is None or operating_cf is None or operating_cf == 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing or zero operating_cash_flow or capital_expenditure'
            )

        # capex is negative, so we take absolute value
        capex_ratio = abs(capex) / operating_cf

        return MetricResult(
            metric_id=self.metric_id,
            value=capex_ratio,
            success=True,
            metadata={
                'capital_expenditure': capex,
                'operating_cash_flow': operating_cf
            }
        )


class CurrentRatioCalculator(MetricCalculator):
    """Calculate Current Ratio (Liquidity Metric)."""

    def __init__(self):
        super().__init__('current_ratio', 'Current Ratio')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        current_assets = self.get_value(raw_data, 'financials.current_assets')
        current_liabilities = self.get_value(raw_data, 'financials.current_liabilities')

        if current_assets is None or current_liabilities is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing required fields: current_assets or current_liabilities'
            )

        current_ratio = self.safe_divide(current_assets, current_liabilities)

        if current_ratio is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Current liabilities is zero'
            )

        # Determine health status
        if current_ratio >= 2.0:
            health = "excellent"
        elif current_ratio >= 1.5:
            health = "good"
        elif current_ratio >= 1.0:
            health = "acceptable"
        else:
            health = "concerning"

        return MetricResult(
            metric_id=self.metric_id,
            value=current_ratio,
            success=True,
            metadata={
                'current_assets': current_assets,
                'current_liabilities': current_liabilities,
                'health': health
            }
        )


# ===== VALUATION METRICS =====

class PriceToEarningsCalculator(MetricCalculator):
    """Calculate Price-to-Earnings Ratio."""

    def __init__(self):
        super().__init__('price_to_earnings', 'Price-to-Earnings Ratio (P/E)')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        price = self.get_value(raw_data, 'price.close')
        net_income = self.get_value(raw_data, 'financials.net_income')
        shares_outstanding = self.get_value(raw_data, 'market_data.shares_outstanding')

        if price is None or net_income is None or shares_outstanding is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing required fields for P/E calculation'
            )

        eps = net_income / shares_outstanding
        pe_ratio = self.safe_divide(price, eps)

        if pe_ratio is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='EPS is zero'
            )

        return MetricResult(
            metric_id=self.metric_id,
            value=pe_ratio,
            success=True,
            metadata={
                'price': price,
                'eps': eps,
                'net_income': net_income,
                'shares_outstanding': shares_outstanding
            }
        )


class ForwardPECalculator(MetricCalculator):
    """Forward P/E Ratio from market data."""

    def __init__(self):
        super().__init__('forward_pe', 'Forward P/E Ratio')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        # Forward P/E comes directly from the market data provider (Yahoo Finance)
        forward_pe = self.get_value(raw_data, 'market_data.forward_pe')

        if forward_pe is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Forward P/E not available from data provider'
            )

        return MetricResult(
            metric_id=self.metric_id,
            value=forward_pe,
            success=True,
            metadata={'source': 'market_data'}
        )


class PriceToBookCalculator(MetricCalculator):
    """Calculate Price-to-Book Ratio."""

    def __init__(self):
        super().__init__('price_to_book', 'Price-to-Book Ratio (P/B)')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        price = self.get_value(raw_data, 'price.close')
        equity = self.get_value(raw_data, 'financials.shareholders_equity')
        shares_outstanding = self.get_value(raw_data, 'market_data.shares_outstanding')

        if price is None or equity is None or shares_outstanding is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing required fields for P/B calculation'
            )

        book_value_per_share = equity / shares_outstanding
        pb_ratio = self.safe_divide(price, book_value_per_share)

        if pb_ratio is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Book value per share is zero'
            )

        return MetricResult(
            metric_id=self.metric_id,
            value=pb_ratio,
            success=True,
            metadata={
                'price': price,
                'book_value_per_share': book_value_per_share,
                'shareholders_equity': equity,
                'shares_outstanding': shares_outstanding
            }
        )


class EVToEBITDACalculator(MetricCalculator):
    """Calculate Enterprise Value / EBITDA."""

    def __init__(self):
        super().__init__('ev_to_ebitda', 'Enterprise Value / EBITDA')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        market_cap = self.get_value(raw_data, 'market_data.market_cap')
        total_debt = self.get_value(raw_data, 'financials.total_debt')
        cash = self.get_value(raw_data, 'financials.cash_and_equivalents')
        ebitda = self.get_value(raw_data, 'financials.ebitda')

        if market_cap is None or ebitda is None or ebitda == 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing required fields or zero EBITDA'
            )

        enterprise_value = market_cap + (total_debt or 0) - (cash or 0)
        ev_to_ebitda = enterprise_value / ebitda

        return MetricResult(
            metric_id=self.metric_id,
            value=ev_to_ebitda,
            success=True,
            metadata={
                'enterprise_value': enterprise_value,
                'market_cap': market_cap,
                'total_debt': total_debt,
                'cash_and_equivalents': cash,
                'ebitda': ebitda
            }
        )


# ===== CAPITAL ALLOCATION METRICS =====

class DividendMetricsCalculator(MetricCalculator):
    """Calculate Dividend Yield and Payout Ratio."""

    def __init__(self):
        super().__init__('dividend_yield_and_payout_ratio', 'Dividend Yield & Payout Ratio')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        price = self.get_value(raw_data, 'price.close')
        dividends_paid = self.get_value(raw_data, 'cash_flow.dividends_paid')
        net_income = self.get_value(raw_data, 'financials.net_income')
        shares_outstanding = self.get_value(raw_data, 'market_data.shares_outstanding')

        dividend_yield = None
        payout_ratio = None

        if dividends_paid and shares_outstanding and price:
            # dividends_paid is negative
            dividend_per_share = abs(dividends_paid) / shares_outstanding
            dividend_yield = dividend_per_share / price

        if dividends_paid and net_income and net_income != 0:
            payout_ratio = abs(dividends_paid) / net_income

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'dividend_yield': dividend_yield,
                'payout_ratio': payout_ratio
            },
            success=True,
            metadata={
                'dividends_paid': dividends_paid,
                'net_income': net_income,
                'shares_outstanding': shares_outstanding,
                'price': price
            }
        )


class DividendHistoryCalculator(MetricCalculator):
    """Analyze Dividend Payment History and Consistency."""

    def __init__(self):
        super().__init__('dividend_history', 'Dividend History Analysis')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        current_dividends = self.get_value(raw_data, 'cash_flow.dividends_paid')
        cash_flow_history = self.get_value(raw_data, 'cash_flow_history', [])

        # Collect all dividend payments
        dividend_payments = []

        for cf in cash_flow_history:
            divs = cf.get('dividends_paid')
            if divs is not None:
                # dividends_paid is negative, take absolute value
                dividend_payments.append(abs(divs))

        # Add current period
        if current_dividends is not None:
            dividend_payments.append(abs(current_dividends))

        if len(dividend_payments) == 0:
            return MetricResult(
                metric_id=self.metric_id,
                value={
                    'pays_dividends': False,
                    'years_of_dividends': 0,
                    'consecutive_years': 0,
                    'growth_years': 0,
                    'avg_growth_rate': None,
                    'is_aristocrat': False,
                    'meets_5year_criteria': False,
                    'classification': 'non_dividend_paying'
                },
                success=True,
                metadata={'dividend_payments': []}
            )

        # Count consecutive years of dividends (from most recent)
        consecutive_years = 0
        for div in reversed(dividend_payments):
            if div > 0:
                consecutive_years += 1
            else:
                break

        # Count years with growing dividends
        growth_years = 0
        for i in range(1, len(dividend_payments)):
            if dividend_payments[i] > dividend_payments[i-1]:
                growth_years += 1

        # Calculate average growth rate (CAGR)
        avg_growth_rate = None
        if len(dividend_payments) >= 2 and dividend_payments[0] > 0:
            years = len(dividend_payments) - 1
            avg_growth_rate = ((dividend_payments[-1] / dividend_payments[0]) ** (1 / years)) - 1

        # Determine classifications
        years_of_dividends = len(dividend_payments)
        is_aristocrat = consecutive_years >= 25
        meets_5year_criteria = consecutive_years >= 5

        # Classification
        if is_aristocrat:
            classification = "dividend_aristocrat"
        elif consecutive_years >= 10:
            classification = "dividend_achiever"
        elif meets_5year_criteria:
            classification = "consistent_payer"
        elif consecutive_years >= 3:
            classification = "regular_payer"
        else:
            classification = "irregular_payer"

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'pays_dividends': True,
                'years_of_dividends': years_of_dividends,
                'consecutive_years': consecutive_years,
                'growth_years': growth_years,
                'avg_growth_rate': avg_growth_rate,
                'is_aristocrat': is_aristocrat,
                'meets_5year_criteria': meets_5year_criteria,
                'classification': classification
            },
            success=True,
            metadata={
                'dividend_payments': dividend_payments,
                'latest_dividend': dividend_payments[-1] if dividend_payments else 0
            }
        )


# ===== VALUATION - ADVANCED METRICS =====

class MarginOfSafetyCalculator(MetricCalculator):
    """Calculate Margin of Safety using DCF method."""

    def __init__(self):
        super().__init__('margin_of_safety', 'Margin of Safety')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        price = self.get_value(raw_data, 'price.close')
        projections = self.get_value(raw_data, 'projections.projected_fcf', [])
        discount_rate = self.get_value(raw_data, 'assumptions.discount_rate', 0.10)
        terminal_growth = self.get_value(raw_data, 'assumptions.terminal_growth', 0.03)
        projection_years = self.get_value(raw_data, 'assumptions.projection_years', 5)

        if not price or not projections:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing price or projected cash flows'
            )

        try:
            # Calculate PV of projected cash flows
            pv_cash_flows = 0
            for t, fcf in enumerate(projections[:projection_years], start=1):
                pv_cash_flows += fcf / ((1 + discount_rate) ** t)

            # Calculate terminal value
            if len(projections) >= projection_years:
                terminal_fcf = projections[projection_years - 1]
                terminal_value = terminal_fcf * (1 + terminal_growth) / (discount_rate - terminal_growth)
                pv_terminal = terminal_value / ((1 + discount_rate) ** projection_years)
            else:
                pv_terminal = 0

            intrinsic_value = pv_cash_flows + pv_terminal

            # Calculate margin of safety
            if intrinsic_value > 0:
                margin_of_safety = 1 - (price / intrinsic_value)
            else:
                margin_of_safety = None

            return MetricResult(
                metric_id=self.metric_id,
                value=margin_of_safety,
                success=True,
                metadata={
                    'intrinsic_value': intrinsic_value,
                    'market_price': price,
                    'pv_cash_flows': pv_cash_flows,
                    'pv_terminal': pv_terminal,
                    'discount_rate': discount_rate
                }
            )
        except Exception as e:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error=f'DCF calculation error: {str(e)}'
            )


class PEGRatioCalculator(MetricCalculator):
    """Calculate PEG Ratio."""

    def __init__(self):
        super().__init__('peg_ratio', 'PEG Ratio')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        # First calculate P/E
        price = self.get_value(raw_data, 'price.close')
        net_income = self.get_value(raw_data, 'financials.net_income')
        shares_outstanding = self.get_value(raw_data, 'market_data.shares_outstanding')

        if not price or not net_income or not shares_outstanding:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing data for P/E calculation'
            )

        eps = net_income / shares_outstanding
        pe_ratio = self.safe_divide(price, eps)

        if not pe_ratio:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Cannot calculate P/E ratio'
            )

        # Calculate EPS growth from history
        financials_history = self.get_value(raw_data, 'financials_history', [])
        if len(financials_history) < 2:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Insufficient historical data for EPS growth'
            )

        # Calculate EPS for each historical period with periods
        eps_data = []
        for fin in financials_history:
            hist_net_income = fin.get('net_income')
            hist_shares = fin.get('shares_outstanding')
            period = fin.get('period', '')
            if hist_net_income and hist_shares and period:
                eps_data.append({
                    'period': period,
                    'eps': hist_net_income / hist_shares
                })

        # Add current EPS
        eps_data.append({
            'period': '9999-12-31',  # Sort current to end
            'eps': eps
        })

        if len(eps_data) < 2:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Cannot calculate EPS growth'
            )

        # Sort by period (oldest to newest)
        eps_data_sorted = sorted(eps_data, key=lambda x: x['period'])

        # Use last 5 years for PEG calculation (industry standard)
        # This avoids issues with old anomalies and gives more relevant growth rate
        eps_data_recent = eps_data_sorted[-6:] if len(eps_data_sorted) > 6 else eps_data_sorted

        # Calculate CAGR from oldest to newest (in recent window)
        years = len(eps_data_recent) - 1
        oldest_eps = eps_data_recent[0]['eps']
        newest_eps = eps_data_recent[-1]['eps']

        eps_cagr = ((newest_eps / oldest_eps) ** (1 / years)) - 1 if oldest_eps > 0 else None

        if eps_cagr is None or eps_cagr <= 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='EPS growth is zero or negative'
            )

        # PEG ratio (growth as percentage)
        eps_growth_pct = eps_cagr * 100

        # Check if growth rate is too low (< 0.5% annualized)
        # Very low or negative growth rates produce unreliable PEG ratios
        if eps_growth_pct < 0.5:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='EPS growth rate too low or negative for PEG calculation',
                metadata={
                    'pe_ratio': pe_ratio,
                    'eps_growth_rate': eps_cagr,
                    'eps_growth_pct': eps_growth_pct
                }
            )

        peg_ratio = pe_ratio / eps_growth_pct

        # Cap PEG ratio at a reasonable maximum (e.g., 100)
        # PEG ratios above 100 are not meaningful for investment decisions
        if peg_ratio > 100:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='PEG ratio too high to be meaningful (growth rate too low)',
                metadata={
                    'pe_ratio': pe_ratio,
                    'eps_growth_rate': eps_cagr,
                    'eps_growth_pct': eps_growth_pct,
                    'calculated_peg': peg_ratio
                }
            )

        return MetricResult(
            metric_id=self.metric_id,
            value=peg_ratio,
            success=True,
            metadata={
                'pe_ratio': pe_ratio,
                'eps_growth_rate': eps_cagr,
                'eps_growth_pct': eps_growth_pct
            }
        )


# ===== GROWTH METRICS =====

class EPSGrowthCalculator(MetricCalculator):
    """Calculate EPS Growth Rate (CAGR)."""

    def __init__(self):
        super().__init__('eps_growth', 'Earnings Per Share Growth')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        net_income = self.get_value(raw_data, 'financials.net_income')
        shares_outstanding = self.get_value(raw_data, 'market_data.shares_outstanding')
        financials_history = self.get_value(raw_data, 'financials_history', [])

        if not net_income or not shares_outstanding:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing current financial data'
            )

        # Calculate EPS for each period
        eps_values = []
        for fin in financials_history:
            hist_net_income = fin.get('net_income')
            hist_shares = fin.get('shares_outstanding')
            if hist_net_income and hist_shares:
                eps_values.append(hist_net_income / hist_shares)

        eps_values.append(net_income / shares_outstanding)

        if len(eps_values) < 2:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Insufficient historical data'
            )

        # Calculate CAGR
        years = len(eps_values) - 1
        if eps_values[0] <= 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Base EPS is zero or negative'
            )

        eps_cagr = ((eps_values[-1] / eps_values[0]) ** (1 / years)) - 1

        return MetricResult(
            metric_id=self.metric_id,
            value=eps_cagr,
            success=True,
            metadata={
                'eps_latest': eps_values[-1],
                'eps_base': eps_values[0],
                'years': years,
                'eps_history': eps_values
            }
        )


class BookValuePerShareGrowthCalculator(MetricCalculator):
    """Calculate Book Value Per Share Growth Rate (CAGR)."""

    def __init__(self):
        super().__init__('book_value_per_share_growth', 'Book Value Per Share Growth')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        equity = self.get_value(raw_data, 'financials.shareholders_equity')
        shares_outstanding = self.get_value(raw_data, 'market_data.shares_outstanding')
        financials_history = self.get_value(raw_data, 'financials_history', [])

        if not equity or not shares_outstanding:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing current financial data'
            )

        # Calculate BVPS for each period
        bvps_values = []
        for fin in financials_history:
            hist_equity = fin.get('shareholders_equity')
            hist_shares = fin.get('shares_outstanding')
            if hist_equity and hist_shares:
                bvps_values.append(hist_equity / hist_shares)

        bvps_values.append(equity / shares_outstanding)

        if len(bvps_values) < 2:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Insufficient historical data'
            )

        # Calculate CAGR
        years = len(bvps_values) - 1
        if bvps_values[0] <= 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Base BVPS is zero or negative'
            )

        bvps_cagr = ((bvps_values[-1] / bvps_values[0]) ** (1 / years)) - 1

        return MetricResult(
            metric_id=self.metric_id,
            value=bvps_cagr,
            success=True,
            metadata={
                'bvps_latest': bvps_values[-1],
                'bvps_base': bvps_values[0],
                'years': years,
                'bvps_history': bvps_values
            }
        )


class EarningsStabilityCalculator(MetricCalculator):
    """Calculate Earnings Stability (positive earnings years)."""

    def __init__(self):
        super().__init__('earnings_stability', 'Earnings Stability')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        net_income = self.get_value(raw_data, 'financials.net_income')
        financials_history = self.get_value(raw_data, 'financials_history', [])

        if net_income is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing current net_income'
            )

        # Count positive earnings years
        positive_years = 0
        total_years = 0
        yearly_earnings = []

        # Historical years
        for fin in financials_history:
            hist_income = fin.get('net_income')
            if hist_income is not None:
                total_years += 1
                yearly_earnings.append(hist_income)
                if hist_income > 0:
                    positive_years += 1

        # Current year
        total_years += 1
        yearly_earnings.append(net_income)
        if net_income > 0:
            positive_years += 1

        if total_years == 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='No earnings data available'
            )

        stability_percentage = positive_years / total_years

        # Determine if meets criteria (8 out of 10 years)
        meets_criteria = False
        if total_years >= 10:
            meets_criteria = positive_years >= 8
        elif total_years >= 5:
            # For fewer years, require proportional consistency
            meets_criteria = stability_percentage >= 0.8

        # Classification
        if stability_percentage >= 0.9:
            classification = "highly_stable"
        elif stability_percentage >= 0.75:
            classification = "stable"
        elif stability_percentage >= 0.5:
            classification = "moderate"
        else:
            classification = "unstable"

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'positive_years': positive_years,
                'total_years': total_years,
                'stability_percentage': stability_percentage,
                'meets_criteria': meets_criteria,
                'classification': classification
            },
            success=True,
            metadata={
                'yearly_earnings': yearly_earnings
            }
        )


# ===== CAPITAL ALLOCATION - ADVANCED =====

class ReturnOnRetainedEarningsCalculator(MetricCalculator):
    """Calculate Return on Retained Earnings (Buffett's $1 test)."""

    def __init__(self):
        super().__init__('return_on_retained_earnings', 'Management Return on Retained Earnings')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        equity_end = self.get_value(raw_data, 'financials.shareholders_equity')
        retained_earnings_end = self.get_value(raw_data, 'financials.retained_earnings')
        financials_history = self.get_value(raw_data, 'financials_history', [])

        if not equity_end or len(financials_history) < 1:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing current data or historical data'
            )

        # Get beginning period values
        equity_begin = financials_history[0].get('shareholders_equity')
        retained_earnings_begin = financials_history[0].get('retained_earnings')

        if not equity_begin or not retained_earnings_begin or not retained_earnings_end:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Missing retained earnings or equity data'
            )

        # Calculate earnings retained
        earnings_retained = retained_earnings_end - retained_earnings_begin

        if earnings_retained <= 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='No earnings retained in period'
            )

        # Calculate value created (book value method)
        value_created = (equity_end - equity_begin) - earnings_retained

        # Return on retained earnings
        return_on_retained = value_created / earnings_retained

        return MetricResult(
            metric_id=self.metric_id,
            value=return_on_retained,
            success=True,
            metadata={
                'earnings_retained': earnings_retained,
                'value_created': value_created,
                'equity_change': equity_end - equity_begin
            }
        )


class WACCvsROICSpreadCalculator(MetricCalculator):
    """Calculate the spread between ROIC and WACC."""

    def __init__(self):
        super().__init__('wacc_vs_roic_spread', 'WACC vs ROIC Spread')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        wacc = self.get_value(raw_data, 'assumptions.wacc')

        # Calculate ROIC first
        roic_calc = ROICCalculator()
        roic_result = roic_calc.calculate(raw_data)

        if not roic_result.success or roic_result.value is None:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Cannot calculate ROIC'
            )

        roic = roic_result.value

        if wacc is None:
            # Default to 8% WACC if not provided
            wacc = 0.08

        spread = roic - wacc

        return MetricResult(
            metric_id=self.metric_id,
            value=spread,
            success=True,
            metadata={
                'roic': roic,
                'wacc': wacc,
                'spread': spread
            }
        )


class TenYearAverageROCECalculator(MetricCalculator):
    """Calculate Ten-Year Average Return on Capital Employed."""

    def __init__(self):
        super().__init__('ten_year_average_roce', 'Ten-Year Average ROCE')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        financials_history = self.get_value(raw_data, 'financials_history', [])

        if len(financials_history) < 2:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Insufficient historical data (need at least 2 years)'
            )

        # Calculate ROCE for each year
        roce_values = []
        for fin in financials_history:
            ebit = fin.get('ebit')
            total_assets = fin.get('total_assets')
            current_liabilities = fin.get('current_liabilities')

            if ebit is not None and total_assets is not None and current_liabilities is not None:
                capital_employed = total_assets - current_liabilities
                if capital_employed > 0:
                    roce = ebit / capital_employed
                    roce_values.append(roce)

        # Add current period
        ebit = self.get_value(raw_data, 'financials.ebit')
        total_assets = self.get_value(raw_data, 'financials.total_assets')
        current_liabilities = self.get_value(raw_data, 'financials.current_liabilities')

        if ebit is not None and total_assets is not None and current_liabilities is not None:
            capital_employed = total_assets - current_liabilities
            if capital_employed > 0:
                roce = ebit / capital_employed
                roce_values.append(roce)

        if len(roce_values) == 0:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Cannot calculate ROCE for any period'
            )

        # Calculate average (limit to 10 years if more available)
        roce_values = roce_values[-10:]
        avg_roce = sum(roce_values) / len(roce_values)

        return MetricResult(
            metric_id=self.metric_id,
            value=avg_roce,
            success=True,
            metadata={
                'years_included': len(roce_values),
                'roce_history': roce_values
            }
        )


# ===== MOAT METRICS =====

class EconomicMoatScoreCalculator(MetricCalculator):
    """Calculate Economic Moat Score based on multiple indicators."""

    def __init__(self):
        super().__init__('economic_moat_score', 'Economic Moat Indicators')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        financials_history = self.get_value(raw_data, 'financials_history', [])
        metrics_history = self.get_value(raw_data, 'metrics_history', [])

        if len(financials_history) < 3:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Need at least 3 years of data for moat analysis'
            )

        # Calculate margin stability (gross margin)
        gross_margins = []
        for fin in financials_history:
            gm = fin.get('gross_margin')
            if gm is not None:
                gross_margins.append(gm)

        current_gm = self.get_value(raw_data, 'financials.gross_margin')
        if current_gm:
            gross_margins.append(current_gm)

        import statistics
        if len(gross_margins) >= 3:
            mean_margin = statistics.mean(gross_margins)
            std_margin = statistics.stdev(gross_margins)
            margin_stability = 1 - (std_margin / mean_margin if mean_margin != 0 else 1)
        else:
            margin_stability = 0

        # Calculate ROIC trend
        roic_values = []
        for metric in metrics_history:
            roic = metric.get('roic')
            if roic is not None:
                roic_values.append(roic)

        # Try to calculate current ROIC
        roic_calc = ROICCalculator()
        roic_result = roic_calc.calculate(raw_data)
        if roic_result.success and roic_result.value:
            roic_values.append(roic_result.value)

        roic_trend = 0
        if len(roic_values) >= 2:
            # Simple linear trend
            n = len(roic_values)
            x_mean = (n - 1) / 2
            y_mean = sum(roic_values) / n
            numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(roic_values))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            roic_trend = numerator / denominator if denominator != 0 else 0

        # Calculate revenue CAGR
        revenues = []
        for fin in financials_history:
            rev = fin.get('revenue')
            if rev is not None:
                revenues.append(rev)

        current_revenue = self.get_value(raw_data, 'financials.revenue')
        if current_revenue:
            revenues.append(current_revenue)

        revenue_cagr = 0
        if len(revenues) >= 2 and revenues[0] > 0:
            years = len(revenues) - 1
            revenue_cagr = ((revenues[-1] / revenues[0]) ** (1 / years)) - 1

        # Composite moat score (weighted)
        # High margins (>0.6), stable margins, positive ROIC trend, healthy revenue growth
        moat_score = 0
        moat_score += min(margin_stability * 0.3, 0.3)  # 30% weight
        moat_score += min(max(roic_trend * 10, 0) * 0.3, 0.3)  # 30% weight
        moat_score += min(max(revenue_cagr, 0) * 0.4, 0.4)  # 40% weight

        # Classify
        if moat_score >= 0.7:
            moat_label = "wide"
        elif moat_score >= 0.4:
            moat_label = "narrow"
        else:
            moat_label = "none"

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'score': moat_score,
                'label': moat_label,
                'margin_stability': margin_stability,
                'roic_trend': roic_trend,
                'revenue_cagr': revenue_cagr
            },
            success=True,
            metadata={
                'gross_margins': gross_margins,
                'roic_values': roic_values
            }
        )


class PiotroskiFScoreCalculator(MetricCalculator):
    """Calculate Piotroski F-Score (9-point fundamental strength test)."""

    def __init__(self):
        super().__init__('piotroski_fscore', 'Piotroski F-Score')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        financials_history = self.get_value(raw_data, 'financials_history', [])
        cash_flow_history = self.get_value(raw_data, 'cash_flow_history', [])

        if len(financials_history) < 1:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Need at least 1 year of historical data for F-Score'
            )

        # Current period values
        net_income = self.get_value(raw_data, 'financials.net_income')
        operating_cf = self.get_value(raw_data, 'financials.operating_cash_flow')
        total_assets = self.get_value(raw_data, 'financials.total_assets')
        current_assets = self.get_value(raw_data, 'financials.current_assets')
        current_liabilities = self.get_value(raw_data, 'financials.current_liabilities')
        total_debt = self.get_value(raw_data, 'financials.total_debt')
        shares_outstanding = self.get_value(raw_data, 'market_data.shares_outstanding')
        gross_margin = self.get_value(raw_data, 'financials.gross_margin')
        revenue = self.get_value(raw_data, 'financials.revenue')

        # Previous period values
        prev_fin = financials_history[-1]
        prev_total_assets = prev_fin.get('total_assets')
        prev_current_ratio = None
        if prev_fin.get('current_assets') and prev_fin.get('current_liabilities'):
            prev_current_ratio = prev_fin['current_assets'] / prev_fin['current_liabilities']
        prev_debt = prev_fin.get('total_debt')
        prev_shares = prev_fin.get('shares_outstanding')
        prev_gross_margin = prev_fin.get('gross_margin')
        prev_revenue = prev_fin.get('revenue')

        score = 0
        components = {}

        # 1. Profitability: Net Income > 0
        if net_income and net_income > 0:
            score += 1
            components['profitable'] = 1
        else:
            components['profitable'] = 0

        # 2. Operating Cash Flow > 0
        if operating_cf and operating_cf > 0:
            score += 1
            components['positive_operating_cf'] = 1
        else:
            components['positive_operating_cf'] = 0

        # 3. ROA Change: Calculate ROA for current and previous year
        current_roa = None
        prev_roa = None
        if net_income and total_assets and total_assets > 0:
            current_roa = net_income / total_assets
        if prev_fin.get('net_income') and prev_total_assets and prev_total_assets > 0:
            prev_roa = prev_fin['net_income'] / prev_total_assets

        if current_roa is not None and prev_roa is not None and current_roa > prev_roa:
            score += 1
            components['roa_improvement'] = 1
        else:
            components['roa_improvement'] = 0

        # 4. Quality of Earnings: Operating CF > Net Income
        if operating_cf and net_income and operating_cf > net_income:
            score += 1
            components['quality_of_earnings'] = 1
        else:
            components['quality_of_earnings'] = 0

        # 5. Long-term Debt / Assets: Decreasing
        current_leverage = None
        prev_leverage = None
        if total_debt is not None and total_assets and total_assets > 0:
            current_leverage = total_debt / total_assets
        if prev_debt is not None and prev_total_assets and prev_total_assets > 0:
            prev_leverage = prev_debt / prev_total_assets

        if current_leverage is not None and prev_leverage is not None and current_leverage < prev_leverage:
            score += 1
            components['decreasing_leverage'] = 1
        else:
            components['decreasing_leverage'] = 0

        # 6. Current Ratio: Increasing
        current_ratio = None
        if current_assets and current_liabilities and current_liabilities > 0:
            current_ratio = current_assets / current_liabilities

        if current_ratio is not None and prev_current_ratio is not None and current_ratio > prev_current_ratio:
            score += 1
            components['improving_liquidity'] = 1
        else:
            components['improving_liquidity'] = 0

        # 7. No New Shares Issued: Shares outstanding not increasing
        if shares_outstanding and prev_shares and shares_outstanding <= prev_shares:
            score += 1
            components['no_dilution'] = 1
        else:
            components['no_dilution'] = 0

        # 8. Gross Margin: Increasing
        if gross_margin is not None and prev_gross_margin is not None and gross_margin > prev_gross_margin:
            score += 1
            components['improving_gross_margin'] = 1
        else:
            components['improving_gross_margin'] = 0

        # 9. Asset Turnover: Increasing (Revenue / Assets)
        current_asset_turnover = None
        prev_asset_turnover = None
        if revenue and total_assets and total_assets > 0:
            current_asset_turnover = revenue / total_assets
        if prev_revenue and prev_total_assets and prev_total_assets > 0:
            prev_asset_turnover = prev_revenue / prev_total_assets

        if current_asset_turnover is not None and prev_asset_turnover is not None and current_asset_turnover > prev_asset_turnover:
            score += 1
            components['improving_asset_turnover'] = 1
        else:
            components['improving_asset_turnover'] = 0

        # Classification
        if score >= 7:
            classification = "strong"
        elif score >= 5:
            classification = "moderate"
        elif score >= 3:
            classification = "weak"
        else:
            classification = "very_weak"

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'score': score,
                'max_score': 9,
                'classification': classification,
                'components': components
            },
            success=True,
            metadata={
                'current_roa': current_roa,
                'prev_roa': prev_roa,
                'current_leverage': current_leverage,
                'prev_leverage': prev_leverage,
                'current_ratio': current_ratio,
                'prev_current_ratio': prev_current_ratio
            }
        )


class ConsistencyScoreCalculator(MetricCalculator):
    """Calculate Consistency of Performance Score."""

    def __init__(self):
        super().__init__('consistency_score', 'Consistency of Performance')

    def calculate(self, raw_data: Dict[str, Any]) -> MetricResult:
        import statistics

        financials_history = self.get_value(raw_data, 'financials_history', [])
        metrics_history = self.get_value(raw_data, 'metrics_history', [])
        cash_flow_history = self.get_value(raw_data, 'cash_flow_history', [])

        if len(financials_history) < 3:
            return MetricResult(
                metric_id=self.metric_id,
                value=None,
                success=False,
                error='Need at least 3 years of data for consistency analysis'
            )

        # Collect historical values for key metrics
        roic_values = []
        roe_values = []
        operating_margins = []
        fcf_values = []

        for metric in metrics_history:
            if metric.get('roic') is not None:
                roic_values.append(metric['roic'])
            if metric.get('roe') is not None:
                roe_values.append(metric['roe'])

        for fin in financials_history:
            if fin.get('operating_margin') is not None:
                operating_margins.append(fin['operating_margin'])

        for cf in cash_flow_history:
            if cf.get('free_cash_flow') is not None:
                fcf_values.append(cf['free_cash_flow'])

        # Add current values
        roic_calc = ROICCalculator()
        roic_result = roic_calc.calculate(raw_data)
        if roic_result.success and roic_result.value:
            roic_values.append(roic_result.value)

        roe_calc = ROECalculator()
        roe_result = roe_calc.calculate(raw_data)
        if roe_result.success and roe_result.value:
            roe_values.append(roe_result.value)

        current_op_margin = self.get_value(raw_data, 'financials.operating_margin')
        if current_op_margin:
            operating_margins.append(current_op_margin)

        fcf_calc = FreeCashFlowCalculator()
        fcf_result = fcf_calc.calculate(raw_data)
        if fcf_result.success and fcf_result.value:
            fcf_values.append(fcf_result.value)

        # Calculate coefficient of variation for each metric
        def calc_cv(values):
            if len(values) < 2:
                return 1.0
            mean = statistics.mean(values)
            if mean == 0:
                return 1.0
            std = statistics.stdev(values)
            return std / abs(mean)

        cv_roic = calc_cv(roic_values) if len(roic_values) >= 2 else 1.0
        cv_roe = calc_cv(roe_values) if len(roe_values) >= 2 else 1.0
        cv_margin = calc_cv(operating_margins) if len(operating_margins) >= 2 else 1.0
        cv_fcf = calc_cv(fcf_values) if len(fcf_values) >= 2 else 1.0

        # Average normalized volatility
        avg_cv = (cv_roic + cv_roe + cv_margin + cv_fcf) / 4

        # Consistency score (inverse of volatility, bounded 0-1)
        consistency_score = max(0, min(1, 1 - avg_cv))

        # Classify
        if consistency_score >= 0.8:
            consistency_label = "highly_consistent"
        elif consistency_score >= 0.6:
            consistency_label = "consistent"
        elif consistency_score >= 0.4:
            consistency_label = "moderate"
        else:
            consistency_label = "volatile"

        return MetricResult(
            metric_id=self.metric_id,
            value={
                'score': consistency_score,
                'label': consistency_label,
                'roic_cv': cv_roic,
                'roe_cv': cv_roe,
                'margin_cv': cv_margin,
                'fcf_cv': cv_fcf
            },
            success=True,
            metadata={
                'roic_values': roic_values,
                'roe_values': roe_values,
                'operating_margins': operating_margins,
                'fcf_values': fcf_values
            }
        )


# ===== CALCULATOR REGISTRY =====

def get_all_calculators() -> List[MetricCalculator]:
    """Get all available metric calculators."""
    return [
        # Profitability
        FreeCashFlowCalculator(),
        ROICCalculator(),
        ROECalculator(),
        OperatingMarginsCalculator(),
        OwnerEarningsCalculator(),

        # Financial Strength
        DebtToEquityCalculator(),
        CapexRatioCalculator(),
        CurrentRatioCalculator(),

        # Valuation
        PriceToEarningsCalculator(),
        ForwardPECalculator(),
        PriceToBookCalculator(),
        EVToEBITDACalculator(),
        MarginOfSafetyCalculator(),
        PEGRatioCalculator(),

        # Growth
        EPSGrowthCalculator(),
        BookValuePerShareGrowthCalculator(),
        EarningsStabilityCalculator(),

        # Capital Allocation
        DividendMetricsCalculator(),
        DividendHistoryCalculator(),
        ReturnOnRetainedEarningsCalculator(),
        WACCvsROICSpreadCalculator(),

        # Long-term Performance
        TenYearAverageROCECalculator(),

        # Moat
        EconomicMoatScoreCalculator(),
        ConsistencyScoreCalculator(),
        PiotroskiFScoreCalculator(),
    ]


def get_calculator_by_id(metric_id: str) -> Optional[MetricCalculator]:
    """Get a specific calculator by metric ID."""
    calculators = get_all_calculators()
    for calc in calculators:
        if calc.metric_id == metric_id:
            return calc
    return None
