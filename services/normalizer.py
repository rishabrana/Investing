"""
Normalizer - Converts raw API responses to consistent schema.

This module normalizes data from different providers into a standard format
that can be stored in JsonStore and consumed by MetricsService.

Each provider returns data in different formats:
- Polygon.io: Uses 'equity', 'revenues', 'net_income_loss'
- Alpha Vantage: Uses 'retainedEarnings', 'interestExpense'
- FMP: Uses 'interestExpense', 'depreciationAndAmortization'

The normalizer converts all of these to standard field names.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from storage.json_store import SourceMetadata


logger = logging.getLogger(__name__)


class Normalizer:
    """
    Normalizes raw API responses to standard schema.

    The normalizer handles:
    1. Field name translation (provider-specific -> standard)
    2. Data type conversion
    3. Derived field calculation (e.g., FCF from operating CF - capex)
    4. Source metadata tracking
    """

    def __init__(self):
        """Initialize normalizer with field mapping rules."""
        # Field name mappings for each provider
        self.field_mappings = {
            'polygon.io': {
                'equity': 'shareholders_equity',
                'liabilities': 'total_liabilities',
                'revenues': 'revenue',
                'net_income_loss': 'net_income',
                'income_tax_expense_benefit': 'income_tax_expense',
                'net_cash_flow_from_operating_activities': 'operating_cash_flow',
            },
            'alpha_vantage': {
                'retainedEarnings': 'retained_earnings',
                'interestExpense': 'interest_expense',
                'depreciationAndAmortization': 'depreciation_amortization',
                'incomeBeforeTax': 'pre_tax_income',
            },
            'financial_modeling_prep': {
                'interestExpense': 'interest_expense',
                'depreciationAndAmortization': 'depreciation_amortization',
                'ebitda': 'ebitda',
                'retainedEarnings': 'retained_earnings',
            },
            'yahoo_finance': {
                'Interest Expense': 'interest_expense',
                'Depreciation': 'depreciation_amortization',
                'Retained Earnings': 'retained_earnings',
                'Operating Income': 'operating_income',
            }
        }

    def normalize(
        self,
        ticker: str,
        raw_data: Dict[str, Any],
        source_metadata: Dict[str, SourceMetadata]
    ) -> Dict[str, Any]:
        """
        Normalize raw API data to standard schema.

        Args:
            ticker: Stock ticker symbol
            raw_data: Raw data from providers
            source_metadata: Source attribution for each field

        Returns:
            Normalized data dictionary ready for storage
        """
        logger.debug(f"Normalizing data for {ticker}")

        normalized = {
            'ticker': ticker.upper(),
            'as_of': self._extract_as_of_date(raw_data),
            'price': {},
            'financials': {},
            'market_data': {},
            'cash_flow': {},
            'assumptions': {},
            'source_metadata': {}
        }

        # Normalize each section
        self._normalize_section(
            raw_data.get('price', {}),
            normalized['price'],
            source_metadata
        )

        self._normalize_section(
            raw_data.get('financials', {}),
            normalized['financials'],
            source_metadata
        )

        self._normalize_section(
            raw_data.get('market_data', {}),
            normalized['market_data'],
            source_metadata
        )

        self._normalize_section(
            raw_data.get('cash_flow', {}),
            normalized['cash_flow'],
            source_metadata
        )

        self._normalize_section(
            raw_data.get('assumptions', {}),
            normalized['assumptions'],
            source_metadata
        )

        # Calculate derived fields
        self._calculate_derived_fields(normalized)

        # Convert source metadata
        normalized['source_metadata'] = {}
        for field_id, meta in source_metadata.items():
            # Handle both dict and SourceMetadata object types
            if isinstance(meta, dict):
                normalized['source_metadata'][field_id] = {
                    'provider': meta.get('provider'),
                    'timestamp': meta.get('timestamp'),
                    'endpoint': meta.get('endpoint')
                }
            else:
                # SourceMetadata object
                normalized['source_metadata'][field_id] = {
                    'provider': meta.provider,
                    'timestamp': meta.timestamp,
                    'endpoint': meta.endpoint
                }

        return normalized

    def _normalize_section(
        self,
        raw_section: Dict[str, Any],
        normalized_section: Dict[str, Any],
        source_metadata: Dict[str, SourceMetadata]
    ):
        """
        Normalize a single section of data.

        Args:
            raw_section: Raw section data
            normalized_section: Target normalized section (modified in place)
            source_metadata: Source attribution
        """
        for field, value in raw_section.items():
            # Translate field name if needed
            standard_name = self._translate_field_name(field, source_metadata.get(field))

            # Store normalized value
            normalized_section[standard_name] = value

    def _translate_field_name(
        self,
        field_name: str,
        metadata: Optional[SourceMetadata]
    ) -> str:
        """
        Translate provider-specific field name to standard name.

        Args:
            field_name: Original field name from provider
            metadata: Source metadata with provider info

        Returns:
            Standard field name
        """
        if not metadata:
            return field_name

        provider = metadata.provider
        mappings = self.field_mappings.get(provider, {})

        return mappings.get(field_name, field_name)

    def _extract_as_of_date(self, raw_data: Dict[str, Any]) -> str:
        """
        Extract the 'as of' date from raw data.

        This is typically the fiscal period end date.

        Args:
            raw_data: Raw data from providers

        Returns:
            ISO date string
        """
        # Try to find date in financials
        financials = raw_data.get('financials', {})
        if 'end_date' in financials:
            return financials['end_date']
        if 'fiscal_year' in financials:
            # Assume end of fiscal year
            year = financials['fiscal_year']
            return f"{year}-12-31"

        # Fallback to current date
        return datetime.utcnow().strftime('%Y-%m-%d')

    def _calculate_derived_fields(self, normalized: Dict[str, Any]):
        """
        Calculate derived fields from normalized data.

        Derived fields that can be calculated immediately:
        - Free Cash Flow = Operating Cash Flow - Capital Expenditure
        - Owner Earnings = Net Income + D&A - Capex (simplified)
        - Pre-tax Income = Net Income + Tax Expense (if not already present)
        - EBIT = Operating Income (if not already present)

        Args:
            normalized: Normalized data (modified in place)
        """
        financials = normalized.get('financials', {})

        # Free Cash Flow
        ocf = financials.get('operating_cash_flow')
        capex = financials.get('capital_expenditure')
        if ocf is not None and capex is not None:
            financials['free_cash_flow'] = ocf - capex
            logger.debug(f"Calculated FCF: {financials['free_cash_flow']}")

        # Pre-tax Income (if not already present)
        if 'pre_tax_income' not in financials:
            net_income = financials.get('net_income')
            tax_expense = financials.get('income_tax_expense')
            if net_income is not None and tax_expense is not None:
                financials['pre_tax_income'] = net_income + tax_expense
                logger.debug(
                    f"Calculated pre-tax income: {financials['pre_tax_income']}"
                )

        # EBIT (if not already present and we have operating income)
        if 'ebit' not in financials:
            operating_income = financials.get('operating_income')
            if operating_income is not None:
                financials['ebit'] = operating_income
                logger.debug(f"Using operating income as EBIT: {financials['ebit']}")

        # Owner Earnings (simplified - full calculation needs more data)
        # owner_earnings = net_income + depreciation - capex + other_non_cash
        net_income = financials.get('net_income')
        depreciation = financials.get('depreciation_amortization')
        if all([net_income, depreciation, capex]):
            # Simplified version without other_non_cash_charges
            financials['owner_earnings_simple'] = (
                net_income + depreciation - capex
            )
            logger.debug(
                f"Calculated owner earnings (simplified): "
                f"{financials['owner_earnings_simple']}"
            )

        # Gross margin
        gross_profit = financials.get('gross_profit')
        revenue = financials.get('revenue')
        if gross_profit is not None and revenue and revenue > 0:
            financials['gross_margin'] = gross_profit / revenue
            logger.debug(f"Calculated gross margin: {financials['gross_margin']:.2%}")

        # Operating margin
        operating_income = financials.get('operating_income')
        if operating_income is not None and revenue and revenue > 0:
            financials['operating_margin'] = operating_income / revenue
            logger.debug(
                f"Calculated operating margin: {financials['operating_margin']:.2%}"
            )

        # Net margin
        if net_income is not None and revenue and revenue > 0:
            financials['net_margin'] = net_income / revenue
            logger.debug(f"Calculated net margin: {financials['net_margin']:.2%}")


# ===== HELPER FUNCTIONS =====

def validate_normalized_data(data: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate normalized data structure.

    Args:
        data: Normalized data dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Required top-level keys
    required_keys = ['ticker', 'as_of']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required field: {key}")

    # Recommended sections
    recommended_sections = [
        'price', 'financials', 'market_data', 'cash_flow'
    ]
    for section in recommended_sections:
        if section not in data or not data[section]:
            logger.warning(f"Empty or missing section: {section}")

    return len(errors) == 0, errors
