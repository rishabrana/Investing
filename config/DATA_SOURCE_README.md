# Data Source Mapping Documentation

## Overview

This document explains the data source mapping configuration for the investing metrics system.

## Files

- **metric_catalog.yaml** - Defines all metrics and their required data points
- **data_source_mapping.yaml** - Maps each data point to its API source

## API Priority Strategy

The system uses a 3-tier fallback strategy:

1. **Primary: Polygon.io** - Official, reliable API for most financial data
2. **Secondary: Alpha Vantage** - For missing fields (interest expense, depreciation, EBITDA, retained earnings)
3. **Tertiary: Yahoo Finance (yfinance)** - Development fallback only

## Data Source Breakdown

### ✅ Polygon.io (Primary) - ~70-80% Coverage

**Available Data:**
- All price data (OHLC)
- Market data (market cap, shares outstanding)
- Balance sheet (assets, liabilities, equity, cash, debt)
- Income statement (revenue, net income, gross profit, operating expenses, tax expense, EPS)
- Cash flow (operating cash flow, net cash flow)
- 10+ years of historical data

### ⚠️ Alpha Vantage (Secondary) - ~15-20% Coverage

**Missing Fields from Polygon.io:**
- `interest_expense` - Income statement
- `depreciation_amortization` - Income/Cash flow statement
- `retained_earnings` - Balance sheet
- `ebitda` - Can calculate or fetch directly
- `other_non_cash_charges` - Cash flow details

### 🔧 Calculated Fields - ~5% Coverage

**Fields that need calculation:**
- `ebit` = operating_income (or net_income + interest_expense + tax_expense)
- `ebitda` = ebit + depreciation_amortization
- `pre_tax_income` = net_income + income_tax_expense
- `gross_margin` = gross_profit / revenue
- `operating_margin` = operating_income / revenue
- `free_cash_flow` = operating_cash_flow - capital_expenditure

### 📝 User Input Required

**Manual data points:**
- All projections (`projected_fcf[]`)
- All assumptions (`discount_rate`, `terminal_growth`, `wacc`, `projection_years`)
- Qualitative indicators

## Usage Example

### Python Implementation

```python
import yaml

# Load data source mapping
with open('config/data_source_mapping.yaml', 'r') as f:
    data_sources = yaml.safe_load(f)

def get_data_point(field_name, ticker):
    """
    Fetch a data point using the priority fallback strategy.
    """
    mapping = data_sources['data_sources'].get(field_name)

    if not mapping:
        raise ValueError(f"Unknown field: {field_name}")

    # Try primary source
    primary = mapping.get('primary')

    if primary == 'polygon.io':
        try:
            return fetch_from_polygon(ticker, mapping)
        except Exception as e:
            print(f"Polygon.io failed: {e}")
            # Fall through to secondary

    if primary == 'alpha_vantage' or mapping.get('secondary') == 'alpha_vantage':
        try:
            return fetch_from_alpha_vantage(ticker, mapping)
        except Exception as e:
            print(f"Alpha Vantage failed: {e}")
            # Fall through to tertiary

    if mapping.get('secondary') == 'yahoo_finance':
        return fetch_from_yahoo_finance(ticker, mapping)

    raise ValueError(f"Could not fetch {field_name} from any source")

# Example usage
ticker_symbol = "AAPL"
close_price = get_data_point('price.close', ticker_symbol)
interest_expense = get_data_point('financials.interest_expense', ticker_symbol)
```

## Field Mapping Reference

### Polygon.io → Standard Names

| Polygon.io Field | Standard Name |
|------------------|---------------|
| `equity` | `shareholders_equity` |
| `liabilities` | `total_liabilities` |
| `revenues` | `revenue` |
| `net_income_loss` | `net_income` |
| `income_tax_expense_benefit` | `income_tax_expense` |
| `net_cash_flow_from_operating_activities` | `operating_cash_flow` |

### Alpha Vantage → Standard Names

| Alpha Vantage Field | Standard Name |
|---------------------|---------------|
| `retainedEarnings` | `retained_earnings` |
| `interestExpense` | `interest_expense` |
| `depreciationAndAmortization` | `depreciation_amortization` |
| `incomeBeforeTax` | `pre_tax_income` |
| `ebitda` | `ebitda` |

### Yahoo Finance → Standard Names

| Yahoo Finance Field | Standard Name |
|---------------------|---------------|
| `"Interest Expense"` | `interest_expense` |
| `"Depreciation"` | `depreciation_amortization` |
| `"Retained Earnings"` | `retained_earnings` |
| `"Operating Income"` | `operating_income` |

## API Endpoints Quick Reference

### Polygon.io

```
Price Data:     /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}
Ticker Details: /v3/reference/tickers/{ticker}
Financials:     /vX/reference/financials?ticker={ticker}&timeframe=annual&limit=10
```

### Alpha Vantage

```
Income Statement: INCOME_STATEMENT&symbol={ticker}
Balance Sheet:    BALANCE_SHEET&symbol={ticker}
Cash Flow:        CASH_FLOW&symbol={ticker}
Company Overview: OVERVIEW&symbol={ticker}
```

### Yahoo Finance (yfinance)

```python
import yfinance as yf
ticker = yf.Ticker("AAPL")

# Access data
ticker.info              # Company info including EBITDA
ticker.financials        # Income statement
ticker.balance_sheet     # Balance sheet
ticker.cashflow          # Cash flow statement
ticker.history()         # Price history
```

## Rate Limits

| API | Free Tier Rate Limit | Notes |
|-----|---------------------|-------|
| Polygon.io | 5 calls/minute | ~5 calls needed per stock for complete data |
| Alpha Vantage | 5 calls/minute, 500/day | Very restrictive, use sparingly |
| Yahoo Finance | Reasonable use | No official limit, unofficial API |

## Implementation Strategy

### Phase 1: Core Data (Polygon.io only)
Implement all metrics that only require Polygon.io data:
- Free Cash Flow
- Return on Equity (ROE)
- Price-to-Earnings (P/E)
- Price-to-Book (P/B)
- Book Value Per Share Growth

### Phase 2: Add Alpha Vantage
Add Alpha Vantage for missing fields:
- Interest Coverage (needs interest_expense)
- Owner Earnings (needs depreciation_amortization)
- Return on Retained Earnings (needs retained_earnings)
- EV/EBITDA (needs ebitda)

### Phase 3: Calculated Metrics
Implement calculation layer:
- EBIT calculation
- EBITDA calculation
- Pre-tax income calculation
- All margin calculations

### Phase 4: User Inputs
Build input system for:
- DCF projections
- Assumptions (WACC, discount rate, etc.)
- Qualitative assessments

## Troubleshooting

### Common Issues

**Issue**: Polygon.io returns empty data for a field
**Solution**: Check if field needs calculation or is in Alpha Vantage

**Issue**: Alpha Vantage rate limit exceeded
**Solution**: Implement caching, reduce API calls, or upgrade plan

**Issue**: Yahoo Finance returns inconsistent data
**Solution**: Use as fallback only, prefer official APIs

### Data Quality Checks

```python
def validate_data_point(value, field_name):
    """Validate fetched data."""
    if value is None:
        raise ValueError(f"Missing data for {field_name}")

    if isinstance(value, (int, float)):
        if value < 0 and field_name in ['revenue', 'assets', 'market_cap']:
            raise ValueError(f"Invalid negative value for {field_name}: {value}")

    return value
```

## Next Steps

1. Implement data fetcher classes for each API
2. Build unified data interface that handles fallbacks
3. Add caching layer to minimize API calls
4. Implement calculation engine for derived metrics
5. Create user input forms for assumptions/projections

## See Also

- [metric_catalog.yaml](metric_catalog.yaml) - Full metric definitions
- [data_source_mapping.yaml](data_source_mapping.yaml) - Complete field mappings
- [polygon_data_availability_analysis.md](../polygon_data_availability_analysis.md) - Detailed Polygon.io analysis
- [free_api_comparison.md](../free_api_comparison.md) - Comprehensive API comparison
