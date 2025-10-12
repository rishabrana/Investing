# Polygon.io Free Tier Data Availability Analysis

> **Note**: For information about alternative free APIs that can fill the gaps, see [free_api_comparison.md](free_api_comparison.md)

## Executive Summary

This document maps all data points required by your metric catalog against Polygon.io's free tier API capabilities.

### Free Tier Limitations
- **Rate Limit**: 5 API calls per minute
- **Historical Data**: 2 years of historical data
- **Data Delay**: End-of-day data only (no real-time intraday)
- **Coverage**: US stocks, forex, and crypto

---

## Data Point Availability Matrix

### ✅ AVAILABLE Data Points

#### Price Data
- ✅ **price.close** - Available via Daily OHLC endpoint
- ✅ **price.open** - Available via Daily OHLC endpoint
- ✅ **price.high** - Available via Daily OHLC endpoint
- ✅ **price.low** - Available via Daily OHLC endpoint

#### Market Data
- ✅ **market_data.market_cap** - Available via Ticker Overview endpoint
- ✅ **market_data.shares_outstanding** - Available as `weighted_shares_outstanding` or `share_class_shares_outstanding`

#### Balance Sheet (via Balance Sheet API)
- ✅ **financials.shareholders_equity** - Available as `equity`
- ✅ **financials.total_liabilities** - Available as `liabilities`
- ✅ **financials.cash_and_equivalents** - Available as `cash`
- ✅ **financials.total_debt** - Available as `long_term_debt` (may need to combine with current portion)
- ✅ **financials.total_assets** - Available as `assets`
- ✅ **financials.current_assets** - Available
- ✅ **financials.current_liabilities** - Available
- ✅ **financials.accounts_receivable** - Available
- ✅ **financials.inventory** - Available
- ✅ **financials.accounts_payable** - Available

#### Income Statement (via Income Statement API)
- ✅ **financials.revenue** - Available as `revenues`
- ✅ **financials.net_income** - Available as `net_income_loss`
- ✅ **financials.operating_income** - May be available as `gross_profit - operating_expenses`
- ✅ **financials.gross_profit** - Available
- ✅ **financials.operating_expenses** - Available
- ✅ **financials.cost_of_revenue** - Available
- ✅ **financials.income_tax_expense** - Available as `income_tax_expense_benefit`
- ✅ **metrics.ttm_eps** - Available as `basic_earnings_per_share` or `diluted_earnings_per_share`

#### Cash Flow Statement (via Cash Flow API)
- ✅ **financials.operating_cash_flow** - Available as `net_cash_flow_from_operating_activities`
- ✅ **financials.capital_expenditure** - Typically part of investing activities (may need calculation)
- ✅ **cash_flow.dividends_paid** - Typically part of financing activities
- ✅ **cash_flow.net_cash_flow** - Available

#### Historical Data
- ✅ **financials_history[]** - Available (10+ years of historical financials)
- ✅ **metrics_history[]** - Can be derived from historical financials

---

### ⚠️ PARTIALLY AVAILABLE / NEEDS CALCULATION

These data points are NOT directly provided but CAN be calculated from available data:

#### Calculated Metrics
- ⚠️ **financials.ebit** - MUST CALCULATE: `operating_income` OR `net_income + interest_expense + income_tax_expense`
- ⚠️ **financials.ebitda** - MUST CALCULATE: `ebit + depreciation + amortization`
- ⚠️ **financials.depreciation_amortization** - NOT directly listed, may need to derive from cash flow
- ⚠️ **financials.pre_tax_income** - MUST CALCULATE: `net_income + income_tax_expense`
- ⚠️ **financials.interest_expense** - NOT explicitly listed, may be in operating expenses detail
- ⚠️ **financials.gross_margin** - MUST CALCULATE: `gross_profit / revenue`
- ⚠️ **financials.operating_margin** - MUST CALCULATE: `operating_income / revenue`
- ⚠️ **financials.retained_earnings** - NOT explicitly listed, may need to track or calculate
- ⚠️ **cash_flow.annual_dividend_per_share** - MUST CALCULATE: `dividends_paid / shares_outstanding`
- ⚠️ **financials.other_non_cash_charges** - May need to derive from cash flow statement details

---

### ❌ NOT AVAILABLE / REQUIRES EXTERNAL DATA

These data points are NOT available in Polygon.io free tier and require either:
1. Manual input/assumptions
2. External data sources
3. Upgraded Polygon.io plan

#### Assumptions & Projections
- ❌ **projections.projected_fcf[]** - You must create/input manually
- ❌ **assumptions.discount_rate** - You must define manually (e.g., WACC calculation)
- ❌ **assumptions.terminal_growth** - You must define manually (typically 2-3%)
- ❌ **assumptions.projection_years** - You must define manually (typically 5-10 years)
- ❌ **assumptions.wacc** - You must calculate manually or use external data

#### Advanced Metrics
- ❌ **metrics.eps_growth_rate** - Must calculate from historical EPS data
- ❌ **metrics.pe** - Must calculate: `price / ttm_eps`
- ❌ **metrics.roic** - Must calculate from available data
- ❌ **metrics.roe** - Must calculate from available data
- ❌ **qualitative.indicators** - External/manual qualitative assessment

---

## Recommended Implementation Strategy

### Phase 1: Core Financial Data ✅
**Status**: Fully supported by Polygon.io free tier

Implement these metrics first as all data is available:
1. Free Cash Flow
2. Return on Equity (ROE)
3. Return on Invested Capital (ROIC)
4. Price-to-Earnings (P/E)
5. Price-to-Book (P/B)
6. EPS Growth
7. Book Value Per Share Growth
8. Operating & Net Margin
9. Debt-to-Equity

### Phase 2: Calculated Metrics ⚠️
**Status**: Requires calculations from available data

These need additional computation logic:
1. EBITDA (calculate from available fields)
2. EV/EBITDA (calculate enterprise value)
3. Interest Coverage (need to find/calculate interest expense)
4. Owner Earnings (need depreciation/amortization breakdown)
5. Capital Expenditure Ratio (extract from cash flow details)

### Phase 3: External/Manual Data ❌
**Status**: Requires manual input or external sources

These cannot be automated with free tier:
1. Margin of Safety (needs projections + assumptions)
2. WACC vs ROIC Spread (needs WACC calculation)
3. Economic Moat Score (qualitative + multi-year analysis)
4. Consistency Score (needs normalized volatility calculations)
5. Return on Retained Earnings (needs careful tracking)

---

## Key Challenges & Solutions

### Challenge 1: EBIT / EBITDA Not Directly Available
**Solution**: Calculate from available fields
- EBIT = Operating Income (or Net Income + Interest + Taxes)
- EBITDA = EBIT + Depreciation + Amortization

### Challenge 2: Depreciation & Amortization Breakdown
**Status**: Not explicitly listed in the glossary
**Solution**:
- May be available in cash flow statement details
- Check if it's embedded in other fields
- Worst case: Use industry averages or manual input

### Challenge 3: Interest Expense Not Explicitly Listed
**Status**: May be embedded in operating expenses
**Solution**:
- Check if available in detailed income statement
- Calculate from balance sheet debt and estimated interest rates
- Use external data source if critical

### Challenge 4: Rate Limits (5 API calls/min)
**Solution**:
- Implement caching strategy
- Batch requests efficiently
- Consider daily/weekly refresh cycles for historical data
- Use background jobs for data updates

### Challenge 5: Retained Earnings Not Listed
**Solution**:
- Calculate: Beginning Retained Earnings + Net Income - Dividends
- Track manually or derive from equity changes
- May need to start tracking from current year forward

---

## API Endpoints You'll Need

### Free Tier Endpoints
1. **Ticker Overview**: `/v3/reference/tickers/{ticker}` - Market cap, shares outstanding
2. **Daily OHLC**: `/v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}` - Stock prices
3. **Balance Sheet**: `/vX/reference/financials` (filtered) - Balance sheet data
4. **Income Statement**: `/vX/reference/financials` (filtered) - Income statement data
5. **Cash Flow**: `/vX/reference/financials` (filtered) - Cash flow data

### Rate Limit Management
With 5 calls/min, you can fetch:
- 1 call: Ticker overview (market cap, shares)
- 1 call: Recent price data
- 1 call: Balance sheet (latest + historical)
- 1 call: Income statement (latest + historical)
- 1 call: Cash flow (latest + historical)

**Total**: All data for 1 stock = ~5 API calls = 1 minute

---

## Verification Checklist

Before implementing, verify these assumptions:

- [ ] Confirm `depreciation_amortization` availability in cash flow API
- [ ] Verify `interest_expense` field exists or determine calculation method
- [ ] Check if `operating_income` is directly available or needs calculation
- [ ] Validate `retained_earnings` availability or calculation method
- [ ] Test API response structure matches glossary documentation
- [ ] Confirm historical data format (10 years as claimed)
- [ ] Verify free tier access to all mentioned endpoints
- [ ] Test rate limiting behavior and error handling

---

## Cost Consideration

If you need more than the free tier provides:

**Polygon.io Starter Plan** (~$29-49/month):
- Higher rate limits
- More historical data
- Potentially more detailed financial fields
- Real-time data options

**Alternative**: Combine Polygon.io free tier with:
- Yahoo Finance API (free, for supplemental data)
- Alpha Vantage (free tier available)
- Manual inputs for assumptions and projections

---

## Conclusion

**Good News**:
- ~70-80% of your required data points are available in Polygon.io's free tier
- Core fundamental financial statements are fully supported
- 10+ years of historical data available

**Challenges**:
- Some fields require calculation (EBIT, EBITDA)
- Depreciation/amortization may need investigation
- All assumptions and projections must be manual
- Rate limits require careful API management

**Recommendation**:
Start with Phase 1 metrics using Polygon.io free tier. This will give you a solid foundation for fundamental analysis. Add calculation logic for Phase 2 metrics. For Phase 3 (projections/assumptions), build a manual input system or use simplified models.
