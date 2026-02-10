# Missing Warren Buffett & Charlie Munger Metrics

This document lists value investing metrics used by Warren Buffett and Charlie Munger that are **not yet implemented** in the stock screener.

## API Availability Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | **Available** - Can be calculated from current API data |
| ⚠️ | **Partial** - Requires additional API or estimated data |
| ❌ | **Not Available** - Data not provided by current APIs |

**Current APIs:** Financial Datasets (primary), Polygon.io, Alpha Vantage, Yahoo Finance

---

## Currently Implemented (29 Metrics)

| Category | Metrics |
|----------|---------|
| **Valuation** | P/E, Forward P/E, P/B, EV/EBITDA, PEG, Margin of Safety |
| **Profitability** | ROIC, ROE, Operating Margin, Net Margin, EPS Growth, BVPS Growth, 10-Yr ROCE |
| **Cash Generation** | FCF, Owner Earnings, CapEx Ratio |
| **Financial Strength** | Debt/Equity, Interest Coverage, Current Ratio |
| **Capital Allocation** | Dividend Yield, Payout Ratio, WACC vs ROIC Spread, RORR |
| **Moat & Quality** | Economic Moat Score, Piotroski F-Score, Consistency Score, Earnings Stability |

---

## Missing Metrics - High Priority

### 1. Competitive Advantage (Moat) Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Gross Profit Margin** | Gross Profit / Revenue | Buffett believes >40% indicates durable competitive advantage | ✅ |
| **SG&A to Gross Profit** | SG&A / Gross Profit | Munger uses this; <30% indicates efficient operations | ⚠️ |
| **R&D to Revenue** | R&D Expense / Revenue | High R&D suggests moat may need constant reinvestment | ❌ |
| **Gross Margin Stability** | Std Dev of Gross Margin (5-10 yr) | Consistent margins = durable moat | ✅ |

### 2. Debt & Leverage Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Long-term Debt to Earnings** | LT Debt / Net Income | Should be <3-4 years; can company easily pay off debt? | ✅ |
| **Debt to EBITDA** | Total Debt / EBITDA | <3x preferred; measures debt serviceability | ✅ |
| **Net Debt to Equity** | (Total Debt - Cash) / Equity | More accurate leverage picture | ✅ |
| **Cash to Debt Ratio** | Cash & Equivalents / Total Debt | >0.5 shows financial flexibility | ✅ |

### 3. Cash Flow Quality Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Price to FCF** | Market Cap / Free Cash Flow | Buffett prefers FCF over earnings for valuation | ✅ |
| **FCF Yield** | FCF / Market Cap | Inverse of P/FCF; >5% is attractive | ✅ |
| **Owner Earnings Yield** | Owner Earnings / Market Cap | Buffett's preferred yield metric | ✅ |
| **Cash Return on Invested Capital (CROIC)** | FCF / Invested Capital | Cash-based ROIC is more reliable | ✅ |
| **Accruals Ratio** | (Net Income - OCF) / Total Assets | Low accruals = higher earnings quality | ✅ |
| **Quality of Earnings** | Operating Cash Flow / Net Income | >1.0 indicates cash-backed earnings | ✅ |

### 4. Efficiency & Productivity Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Asset Turnover** | Revenue / Average Total Assets | How efficiently assets generate revenue | ✅ |
| **Inventory Turnover** | COGS / Average Inventory | Higher = better inventory management | ✅ |
| **Receivables Turnover** | Revenue / Average Receivables | Higher = faster cash collection | ✅ |
| **Days Sales Outstanding (DSO)** | (Receivables / Revenue) × 365 | Lower = better; cash collection speed | ✅ |
| **Days Inventory Outstanding (DIO)** | (Inventory / COGS) × 365 | Lower = better inventory efficiency | ✅ |
| **Cash Conversion Cycle** | DSO + DIO - DPO | Lower = more efficient working capital | ✅ |
| **Revenue per Employee** | Revenue / # Employees | Productivity and scalability indicator | ❌ |

### 5. Capital Efficiency Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Return on Tangible Assets (ROTA)** | Net Income / (Assets - Goodwill - Intangibles) | True asset efficiency without acquisition premiums | ❌ |
| **Return on Tangible Equity (ROTE)** | Net Income / Tangible Equity | ROE without goodwill distortions | ❌ |
| **Goodwill to Assets Ratio** | Goodwill / Total Assets | High ratio may indicate overpaid acquisitions | ❌ |
| **CapEx to Depreciation** | CapEx / Depreciation | <1.5 = maintenance mode; >2 = growth mode | ✅ |
| **Sustainable Growth Rate** | ROE × (1 - Dividend Payout) | Max growth without external financing | ✅ |

### 6. Shareholder Value Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Buyback Yield** | (Shares Retired × Price) / Market Cap | Value returned via buybacks | ⚠️ |
| **Total Shareholder Return Yield** | Dividend Yield + Buyback Yield | Complete capital return picture | ⚠️ |
| **Buyback Effectiveness** | EPS Growth vs Shares Outstanding Change | Did buybacks create per-share value? | ✅ |
| **Look-Through Earnings** | Pro-rata share of investee earnings | For companies with equity investments | ❌ |

### 7. Risk & Safety Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Altman Z-Score** | Multi-factor bankruptcy predictor | Z > 3 = safe; Z < 1.8 = distress risk | ✅ |
| **Beneish M-Score** | Earnings manipulation detector | M > -2.22 = potential manipulation | ❌ |
| **Sloan Ratio** | (Net Income - FCF) / Total Assets | High = earnings may be low quality | ✅ |
| **Operating Leverage** | % Change in EBIT / % Change in Revenue | Higher = more earnings volatility | ✅ |

### 8. Intrinsic Value Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Graham Number** | √(22.5 × EPS × BVPS) | Benjamin Graham's intrinsic value estimate | ✅ |
| **Earnings Power Value (EPV)** | Adjusted Earnings / WACC | Value based on current earnings, no growth | ✅ |
| **Net-Net Working Capital** | (Current Assets - Total Liabilities) / Shares | Graham's cigar butt valuation | ✅ |
| **Liquidation Value** | Book Value - Intangibles - Liabilities | Floor value in worst case | ❌ |

### 9. Management Quality Metrics

| Metric | Formula | Why Buffett/Munger Use It | API |
|--------|---------|---------------------------|-----|
| **Insider Ownership %** | Insider Shares / Total Shares | Skin in the game; >5% preferred | ❌ |
| **CEO Pay to Net Income** | CEO Compensation / Net Income | <3% shows aligned incentives | ❌ |
| **Incremental ROIC** | Δ EBIT / Δ Invested Capital | How well new capital is deployed | ✅ |
| **Acquisition Success Rate** | Post-acquisition ROIC vs Pre | Track record on M&A | ⚠️ |

---

## Missing Metrics - Medium Priority

### 10. Industry-Specific Metrics

| Metric | Applies To | Formula | API |
|--------|------------|---------|-----|
| **Insurance Float** | Insurance | Premium Revenue - Claims - Expenses | ❌ |
| **Combined Ratio** | Insurance | (Claims + Expenses) / Premiums; <100% = underwriting profit | ❌ |
| **Loan Loss Provision Ratio** | Banks | Provisions / Total Loans | ❌ |
| **Net Interest Margin (NIM)** | Banks | (Interest Income - Interest Expense) / Avg Assets | ❌ |
| **Same-Store Sales Growth** | Retail | YoY Revenue Growth (existing locations) | ❌ |
| **Subscriber Churn Rate** | SaaS/Subscription | Lost Subscribers / Total Subscribers | ❌ |
| **Customer Acquisition Cost (CAC)** | SaaS/Tech | Sales & Marketing / New Customers | ❌ |
| **Lifetime Value (LTV)** | SaaS/Tech | Avg Revenue per User × Avg Customer Lifespan | ❌ |

### 11. Trend & Momentum Metrics

| Metric | Formula | Why It Matters | API |
|--------|---------|----------------|-----|
| **5-Year Revenue CAGR** | (End/Start)^(1/5) - 1 | Long-term growth trajectory | ✅ |
| **5-Year FCF CAGR** | FCF growth rate | Cash generation trend | ✅ |
| **Margin Expansion Rate** | Δ Operating Margin / Year | Improving or deteriorating economics | ✅ |
| **ROIC Trend** | 5-year ROIC trajectory | Capital efficiency direction | ✅ |

---

## Summary: Top 15 Metrics to Add

Based on Buffett's letters and Munger's investment principles, these should be prioritized:

| Priority | Metric | Reason | API |
|----------|--------|--------|-----|
| 1 | **Gross Profit Margin** | Core moat indicator (>40% = durable advantage) | ✅ |
| 2 | **Price to FCF** | Buffett's preferred valuation metric | ✅ |
| 3 | **FCF Yield** | Quick assessment of cash return potential | ✅ |
| 4 | **Long-term Debt to Earnings** | Must be <4 years payoff capability | ✅ |
| 5 | **Quality of Earnings (OCF/NI)** | Cash backing for reported earnings | ✅ |
| 6 | **SG&A to Gross Profit** | Munger's efficiency test (<30%) | ⚠️ |
| 7 | **Return on Tangible Equity** | True profitability without goodwill | ❌ |
| 8 | **Altman Z-Score** | Bankruptcy risk screening | ✅ |
| 9 | **Buyback Yield** | Total shareholder return picture | ⚠️ |
| 10 | **Insider Ownership %** | Management alignment | ❌ |
| 11 | **Cash Conversion Cycle** | Working capital efficiency | ✅ |
| 12 | **Graham Number** | Classic intrinsic value estimate | ✅ |
| 13 | **CROIC** | Cash-based capital efficiency | ✅ |
| 14 | **Gross Margin Stability** | Moat durability over time | ✅ |
| 15 | **Incremental ROIC** | Capital allocation skill | ✅ |

---

## Quick Implementation Summary

### Ready to Implement (28 metrics) ✅
All data available from current APIs (Financial Datasets, Polygon, Alpha Vantage):

**Valuation:** Price to FCF, FCF Yield, Owner Earnings Yield, Graham Number, EPV, Net-Net Working Capital

**Profitability:** Gross Profit Margin, Gross Margin Stability, CROIC, Asset Turnover, Incremental ROIC

**Leverage:** Long-term Debt to Earnings, Debt to EBITDA, Net Debt to Equity, Cash to Debt Ratio

**Efficiency:** Inventory Turnover, Receivables Turnover, DSO, DIO, Cash Conversion Cycle

**Quality:** Quality of Earnings, Accruals Ratio, Sloan Ratio, Operating Leverage

**Risk:** Altman Z-Score

**Capital:** CapEx to Depreciation, Sustainable Growth Rate, Buyback Effectiveness

**Trends:** 5-Year Revenue CAGR, 5-Year FCF CAGR, Margin Expansion Rate, ROIC Trend

### Partial Data Available (4 metrics) ⚠️
Can be estimated or derived with some assumptions:

- **SG&A to Gross Profit** - Operating expenses available, but SG&A not broken out
- **Buyback Yield** - Can calculate from shares outstanding changes over time
- **Total Shareholder Return Yield** - Depends on buyback yield calculation
- **Acquisition Success Rate** - Requires manual identification of acquisition dates

### Not Available (12 metrics) ❌
Would require additional API integrations (see data sources below).

---

## Data Sources for Missing Metrics

### Partial Metrics (⚠️) - Where to Get the Data

| Metric | Missing Data | Recommended API | Notes |
|--------|--------------|-----------------|-------|
| **SG&A to Gross Profit** | SG&A breakdown | [Financial Modeling Prep](https://financialmodelingprep.com) | Income statement includes SG&A separately |
| **Buyback Yield** | Shares repurchased | [Polygon.io](https://polygon.io) or [SEC-API](https://sec-api.io) | Track shares outstanding changes or parse 10-K |
| **Total Shareholder Return** | Buyback data | Same as above | Combine with existing dividend data |
| **Acquisition Success Rate** | M&A dates | [Finnhub](https://finnhub.io) | Has merger/acquisition data endpoint |

### Not Available Metrics (❌) - Where to Get the Data

| Metric | Missing Data | Recommended API | Pricing |
|--------|--------------|-----------------|---------|
| **R&D to Revenue** | R&D expense | [SEC EDGAR](https://data.sec.gov) | **FREE** |
| | | [Financial Modeling Prep](https://financialmodelingprep.com) | Free: 250/day |
| **Revenue per Employee** | Employee count | [Financial Modeling Prep](https://financialmodelingprep.com) | Free: 250/day |
| | | [Finnhub](https://finnhub.io) | **FREE**: 60/min |
| **Return on Tangible Equity** | Goodwill, Intangibles | [SEC EDGAR](https://data.sec.gov) | **FREE** (XBRL data) |
| | | [Financial Modeling Prep](https://financialmodelingprep.com) | Free: 250/day |
| **Goodwill to Assets** | Goodwill | [SEC EDGAR](https://data.sec.gov) | **FREE** (XBRL tag: `Goodwill`) |
| **Insider Ownership %** | Insider holdings | [SEC EDGAR](https://data.sec.gov) | **FREE** (Form 3, 4, 5) |
| | | [Finnhub](https://finnhub.io) | **FREE**: 60/min |
| **CEO Pay to Net Income** | Exec compensation | [Financial Modeling Prep](https://financialmodelingprep.com) | Free: 250/day |
| | | SEC EDGAR DEF 14A | **FREE** (Proxy parsing) |
| **Look-Through Earnings** | Investee breakdown | Manual / SEC 10-K | Not available via API |
| **Beneish M-Score** | 8 specific ratios | [SEC EDGAR](https://data.sec.gov) + calculation | **FREE** |
| **Liquidation Value** | Intangibles detail | [SEC EDGAR](https://data.sec.gov) | **FREE** (XBRL data) |
| **Industry-Specific** | Specialized data | Industry-specific APIs | See below |

### Industry-Specific Data Sources

| Industry | Metrics | Data Source |
|----------|---------|-------------|
| **Insurance** | Float, Combined Ratio | [S&P Capital IQ](https://www.spglobal.com/marketintelligence), SEC 10-K parsing |
| **Banks** | NIM, Loan Loss Provisions | [Federal Reserve FRED](https://fred.stlouisfed.org), Bank 10-Q filings |
| **Retail** | Same-Store Sales | Company earnings releases, [Placer.ai](https://placer.ai) |
| **SaaS** | Churn, CAC, LTV | Not publicly available (internal metrics) |

---

## Recommended API Strategy

### Option 1: Add Financial Modeling Prep (Best Value)
**Cost:** Free tier (250 calls/day) or $19/month
**Unlocks:** 8 missing metrics
- R&D expense
- SG&A breakdown
- Employee count
- Goodwill & intangibles
- Executive compensation
- Detailed balance sheet

Already in your config but not implemented. Would unlock most missing metrics.

### Option 2: Add Finnhub (Already Planned)
**Cost:** Free tier (60 calls/min)
**Unlocks:** 3 missing metrics
- Insider transactions/ownership
- M&A data
- Employee count (backup)

Also already in your config as quinary provider.

### Option 3: Use SEC EDGAR API (FREE - RECOMMENDED)
**Cost:** FREE (official SEC.gov API)
**Unlocks:** 7 missing metrics
- Goodwill & Intangibles (XBRL tags)
- R&D Expense (XBRL tag: `ResearchAndDevelopmentExpense`)
- SG&A Expense (XBRL tag: `SellingGeneralAndAdministrativeExpense`)
- Insider Ownership (Form 3, 4, 5 filings)
- All XBRL financial statement data

**Endpoints:**
- `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` - All financial data
- `https://data.sec.gov/submissions/CIK{cik}.json` - Filing history + Form 4

### Option 4: Add Intrinio (Most Comprehensive)
**Cost:** $3,000-9,000/year
**Unlocks:** All missing metrics
- Most detailed financial statements
- Goodwill, intangibles, R&D all included
- Best for institutional-grade analysis

---

## Quick Wins: Implement These First

| Priority | API to Add | Metrics Unlocked | Cost | Effort |
|----------|------------|------------------|------|--------|
| 1 | **SEC EDGAR** | R&D, SG&A, Goodwill, Intangibles, Insider Ownership | **FREE** | Medium |
| 2 | **Finnhub** | M&A Data, Insider Transactions (backup) | **FREE** | Low |
| 3 | **Financial Modeling Prep** | Employee Count, Exec Comp, Beneish data | Free/$19 | Low |

With SEC EDGAR + Finnhub integration, you'd unlock **9 of the 16 missing metrics for FREE**.

---

## References

- Warren Buffett's Annual Letters to Shareholders (1977-2024)
- "Poor Charlie's Almanack" - Charlie Munger
- "The Warren Buffett Way" - Robert Hagstrom
- "Security Analysis" - Benjamin Graham & David Dodd
- "The Intelligent Investor" - Benjamin Graham
