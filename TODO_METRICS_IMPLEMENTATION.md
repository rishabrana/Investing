# Metrics Implementation Todo List

## Overview

**Total New Metrics to Add:** 44
**APIs to Implement:** 3 (SEC EDGAR, Financial Modeling Prep, Finnhub)

---

## Phase 1: SEC EDGAR API Integration (FREE)

### API Setup

- [ ] Create `clients/sec_edgar_client.py`
- [ ] Add SEC EDGAR to `config/data_source_mapping.yaml`
- [ ] Implement rate limiting (10 requests/second max)
- [ ] Add User-Agent header (required by SEC)

### SEC EDGAR Endpoints

| Endpoint | URL Pattern | Data Provided |
|----------|-------------|---------------|
| Company Facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` | All XBRL financial data |
| Company Concept | `https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json` | Specific financial concepts |
| Submissions | `https://data.sec.gov/submissions/CIK{cik}.json` | Filing history, Form 4 links |
| Frames | `https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/USD/CY{year}.json` | Cross-company data |

### Implementation Tasks

- [ ] Implement CIK lookup from ticker symbol
- [ ] Fetch Company Facts JSON for full financial data
- [ ] Parse XBRL tags for missing balance sheet items:
  - [ ] `Goodwill`
  - [ ] `IntangibleAssetsNetExcludingGoodwill`
  - [ ] `ResearchAndDevelopmentExpense`
  - [ ] `SellingGeneralAndAdministrativeExpense`
- [ ] Parse Form 4 filings for insider transactions
- [ ] Cache CIK mappings locally

### Metrics Unlocked by SEC EDGAR (FREE)

| Metric | XBRL Tag | Status |
|--------|----------|--------|
| R&D to Revenue | `ResearchAndDevelopmentExpense` | [ ] |
| SG&A to Gross Profit | `SellingGeneralAndAdministrativeExpense` | [ ] |
| Goodwill to Assets | `Goodwill` | [ ] |
| Return on Tangible Assets | `Goodwill` + `IntangibleAssetsNetExcludingGoodwill` | [ ] |
| Return on Tangible Equity | Same as above | [ ] |
| Liquidation Value | `IntangibleAssetsNetExcludingGoodwill` | [ ] |
| Insider Ownership % | Form 3/4/5 filings | [ ] |

---

## Phase 2: Financial Modeling Prep Integration

### API Setup

- [ ] Implement `clients/fmp_client.py` (already in config, not implemented)
- [ ] Add API key management
- [ ] Implement rate limiting (5 calls/second, 250/day free tier)

### FMP Endpoints Needed

| Endpoint | URL Pattern | Data Provided |
|----------|-------------|---------------|
| Company Profile | `/api/v3/profile/{ticker}` | Employee count, sector, beta |
| Income Statement | `/api/v3/income-statement/{ticker}` | R&D, SG&A breakdown |
| Balance Sheet | `/api/v3/balance-sheet-statement/{ticker}` | Goodwill, intangibles |
| Key Executives | `/api/v3/key-executives/{ticker}` | CEO compensation |
| Stock Peers | `/api/v3/stock_peers` | Peer comparison |

### Metrics Unlocked by FMP

| Metric | Endpoint | Status |
|--------|----------|--------|
| Revenue per Employee | Company Profile (`fullTimeEmployees`) | [ ] |
| CEO Pay to Net Income | Key Executives | [ ] |
| Beneish M-Score components | Income Statement + Balance Sheet | [ ] |

---

## Phase 3: Finnhub Integration

### API Setup

- [ ] Implement `clients/finnhub_client.py` (already in config, not implemented)
- [ ] Add API key management
- [ ] Implement rate limiting (60 calls/min free tier)

### Finnhub Endpoints Needed

| Endpoint | URL Pattern | Data Provided |
|----------|-------------|---------------|
| Insider Transactions | `/stock/insider-transactions` | Form 4 transactions |
| Company Profile | `/stock/profile2` | Employee count (backup) |
| Mergers & Acquisitions | `/stock/merger` | M&A history |

### Metrics Unlocked by Finnhub

| Metric | Endpoint | Status |
|--------|----------|--------|
| Insider Transactions | insider-transactions | [ ] |
| Acquisition Success Rate | merger endpoint | [ ] |

---

## Phase 4: Metric Calculators

### Valuation Metrics (6 new)

- [ ] `PriceToFCFCalculator` - Market Cap / FCF
- [ ] `FCFYieldCalculator` - FCF / Market Cap
- [ ] `OwnerEarningsYieldCalculator` - Owner Earnings / Market Cap
- [ ] `GrahamNumberCalculator` - √(22.5 × EPS × BVPS)
- [ ] `EPVCalculator` - Adjusted Earnings / WACC
- [ ] `NetNetWorkingCapitalCalculator` - (Current Assets - Total Liabilities) / Shares

### Profitability Metrics (5 new)

- [ ] `GrossProfitMarginCalculator` - Gross Profit / Revenue
- [ ] `GrossMarginStabilityCalculator` - Std Dev of Gross Margin (5-10 yr)
- [ ] `CROICCalculator` - FCF / Invested Capital
- [ ] `AssetTurnoverCalculator` - Revenue / Total Assets
- [ ] `IncrementalROICCalculator` - Δ EBIT / Δ Invested Capital

### Leverage Metrics (4 new)

- [ ] `LongTermDebtToEarningsCalculator` - LT Debt / Net Income
- [ ] `DebtToEBITDACalculator` - Total Debt / EBITDA
- [ ] `NetDebtToEquityCalculator` - (Total Debt - Cash) / Equity
- [ ] `CashToDebtRatioCalculator` - Cash / Total Debt

### Efficiency Metrics (6 new)

- [ ] `InventoryTurnoverCalculator` - COGS / Inventory
- [ ] `ReceivablesTurnoverCalculator` - Revenue / Receivables
- [ ] `DSOCalculator` - (Receivables / Revenue) × 365
- [ ] `DIOCalculator` - (Inventory / COGS) × 365
- [ ] `DPOCalculator` - (Payables / COGS) × 365
- [ ] `CashConversionCycleCalculator` - DSO + DIO - DPO

### Quality Metrics (4 new)

- [ ] `QualityOfEarningsCalculator` - OCF / Net Income
- [ ] `AccrualsRatioCalculator` - (Net Income - OCF) / Total Assets
- [ ] `SloanRatioCalculator` - (Net Income - FCF) / Total Assets
- [ ] `OperatingLeverageCalculator` - % Change EBIT / % Change Revenue

### Risk Metrics (1 new)

- [ ] `AltmanZScoreCalculator` - Multi-factor formula

### Capital Metrics (3 new)

- [ ] `CapExToDepreciationCalculator` - CapEx / Depreciation
- [ ] `SustainableGrowthRateCalculator` - ROE × (1 - Payout)
- [ ] `BuybackEffectivenessCalculator` - EPS Growth vs Shares Change

### Trend Metrics (4 new)

- [ ] `RevenueCAGRCalculator` - 5-year revenue CAGR
- [ ] `FCFCAGRCalculator` - 5-year FCF CAGR
- [ ] `MarginExpansionCalculator` - Δ Operating Margin / Year
- [ ] `ROICTrendCalculator` - 5-year ROIC trajectory

### Metrics Requiring New APIs (11 new)

After SEC EDGAR + FMP + Finnhub integration:

- [ ] `RDToRevenueCalculator` - R&D / Revenue (SEC EDGAR)
- [ ] `SGAToGrossProfitCalculator` - SG&A / Gross Profit (SEC EDGAR)
- [ ] `GoodwillToAssetsCalculator` - Goodwill / Assets (SEC EDGAR)
- [ ] `ROTACalculator` - Net Income / Tangible Assets (SEC EDGAR)
- [ ] `ROTECalculator` - Net Income / Tangible Equity (SEC EDGAR)
- [ ] `LiquidationValueCalculator` - Book Value - Intangibles (SEC EDGAR)
- [ ] `InsiderOwnershipCalculator` - Insider Shares / Total (SEC EDGAR + Finnhub)
- [ ] `RevenuePerEmployeeCalculator` - Revenue / Employees (FMP)
- [ ] `CEOPayRatioCalculator` - CEO Comp / Net Income (FMP)
- [ ] `BuybackYieldCalculator` - Buyback Value / Market Cap (SEC EDGAR)
- [ ] `AcquisitionSuccessCalculator` - Post-M&A ROIC vs Pre (Finnhub)

---

## Phase 5: Frontend Components

### New Metric Display Components

- [ ] Add Gross Profit Margin to `ProfitabilityMetrics.tsx`
- [ ] Create `EfficiencyMetrics.tsx` component
- [ ] Create `QualityMetrics.tsx` component
- [ ] Add Altman Z-Score to `FinancialStrengthMetrics.tsx`
- [ ] Add insider ownership to existing ownership display

### Screener Criteria Updates

- [ ] Add Gross Profit Margin > 40% filter
- [ ] Add Quality of Earnings > 1.0 filter
- [ ] Add Altman Z-Score > 3.0 filter
- [ ] Add Long-term Debt to Earnings < 4 filter

---

## Phase 6: Testing & Documentation

- [ ] Unit tests for SEC EDGAR client
- [ ] Unit tests for new metric calculators
- [ ] Integration tests for API fallbacks
- [ ] Update `config/metric_catalog.yaml` with new metrics
- [ ] Update frontend `metricInfo.ts` with descriptions

---

## Implementation Priority

### Week 1: SEC EDGAR (High Value, Free)
1. [ ] SEC EDGAR client implementation
2. [ ] CIK lookup and caching
3. [ ] XBRL parsing for Goodwill, R&D, SG&A, Intangibles
4. [ ] Form 4 parsing for insider transactions

### Week 2: Ready-to-Implement Metrics (28 metrics)
1. [ ] Implement all calculators using existing API data
2. [ ] Add to metric catalog
3. [ ] Frontend display components

### Week 3: FMP + Finnhub Integration
1. [ ] FMP client (employee count, exec comp)
2. [ ] Finnhub client (M&A data)
3. [ ] Remaining calculators

### Week 4: Frontend & Testing
1. [ ] New frontend components
2. [ ] Screener filter updates
3. [ ] Testing and documentation

---

## SEC EDGAR Implementation Details

### CIK Lookup

```python
# Get CIK from ticker
# https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&dateb=&owner=include&count=40&output=json
```

### Company Facts Example

```python
# https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json (Apple)
# Returns all XBRL facts including:
# - us-gaap:Goodwill
# - us-gaap:ResearchAndDevelopmentExpense
# - us-gaap:SellingGeneralAndAdministrativeExpense
# - us-gaap:IntangibleAssetsNetExcludingGoodwill
```

### Required Headers

```python
headers = {
    'User-Agent': 'YourAppName contact@email.com',  # Required by SEC
    'Accept': 'application/json'
}
```

### Rate Limiting

- Max 10 requests per second
- No API key required
- Use exponential backoff on 429 errors

---

## Cost Summary

| API | Cost | Metrics Unlocked |
|-----|------|------------------|
| SEC EDGAR | **FREE** | 7 metrics (Goodwill, R&D, SG&A, Intangibles, Insider) |
| Financial Modeling Prep | Free (250/day) or $19/mo | 3 metrics (Employees, Exec Comp, Beneish) |
| Finnhub | **FREE** (60/min) | 2 metrics (M&A, Insider backup) |

**Total: $0-19/month for all missing metrics**

---

## Quick Reference: All 44 New Metrics

### Already Have Data (28) ✅
1. Price to FCF
2. FCF Yield
3. Owner Earnings Yield
4. Graham Number
5. EPV
6. Net-Net Working Capital
7. Gross Profit Margin
8. Gross Margin Stability
9. CROIC
10. Asset Turnover
11. Incremental ROIC
12. Long-term Debt to Earnings
13. Debt to EBITDA
14. Net Debt to Equity
15. Cash to Debt Ratio
16. Inventory Turnover
17. Receivables Turnover
18. DSO
19. DIO
20. Cash Conversion Cycle
21. Quality of Earnings
22. Accruals Ratio
23. Sloan Ratio
24. Operating Leverage
25. Altman Z-Score
26. CapEx to Depreciation
27. Sustainable Growth Rate
28. Buyback Effectiveness

### Need SEC EDGAR (7) 🆓
29. R&D to Revenue
30. SG&A to Gross Profit
31. Goodwill to Assets
32. Return on Tangible Assets
33. Return on Tangible Equity
34. Liquidation Value
35. Insider Ownership %

### Need FMP (3) 💰
36. Revenue per Employee
37. CEO Pay to Net Income
38. Beneish M-Score

### Need Finnhub (2) 🆓
39. Buyback Yield
40. Acquisition Success Rate

### Trend Metrics (4) ✅
41. 5-Year Revenue CAGR
42. 5-Year FCF CAGR
43. Margin Expansion Rate
44. ROIC Trend
