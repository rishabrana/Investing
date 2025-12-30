# Missing Data Points & Metrics Analysis

## Executive Summary

After analyzing the codebase and comparing against the Stock Screeners requirements, here's the status:

- **Value Investing Screener**: ✅ 85% Complete (8.5/10 metrics available)
- **Momentum Trading Screener**: ❌ 10% Complete (1/10 metrics available)

---

## 1. VALUE INVESTING SCREENER - Data Availability

### ✅ AVAILABLE (8.5/10 metrics)

| Metric | Status | Implementation |
|--------|--------|----------------|
| **P/E Ratio** | ✅ Complete | `PERatioCalculator` - price / (net_income / shares) |
| **P/B Ratio** | ✅ Complete | `PBRatioCalculator` - price / (equity / shares) |
| **FCF Yield** | ✅ Complete | Calculate from `FreecashFlowCalculator` / market_cap |
| **ROE** | ✅ Complete | `ROECalculator` - net_income / shareholders_equity |
| **Debt-to-Equity** | ✅ Complete | `DebtToEquityCalculator` - total_liabilities / equity |
| **Dividend Yield** | ✅ Complete | `DividendYieldCalculator` - (dividends/shares) / price |
| **PEG Ratio** | ✅ Complete | `PEGRatioCalculator` - P/E / (EPS_growth * 100) |
| **Operating Margin** | ✅ Complete | Built-in field: `financials.operating_margin` |
| **Current Ratio** | ⚠️ Partial | Can calculate: current_assets / current_liabilities |
| **Earnings Stability** | ⚠️ Partial | Have 10-year history, need counting logic |

### ❌ MISSING (1.5/10 metrics)

#### 1. **Current Ratio Calculator** - Easy to Add
```python
# Formula: Current Assets / Current Liabilities
# Required fields: ✅ Already available
- financials.current_assets
- financials.current_liabilities

# Action: Create CurrentRatioCalculator
```

#### 2. **Earnings Stability Counter** - Easy to Add
```python
# Requirement: Positive earnings in 8 of last 10 years
# Required fields: ✅ Already available
- financials_history[].net_income (10 years)

# Action: Create EarningsStabilityCalculator
# Returns: {
#   "positive_years": 9,
#   "total_years": 10,
#   "stability_percentage": 0.90,
#   "meets_criteria": true  # 8+ years
# }
```

#### 3. **Dividend History Analysis** - Moderate to Add
```python
# Requirement: 5+ years consistent/growing dividends
# Currently have: Single period dividend data
# Required fields: ❌ Need historical dividends
- cash_flow_history[].dividends_paid  # ✅ Already in API data

# Action: Create DividendHistoryCalculator
# Returns: {
#   "years_of_dividends": 10,
#   "consecutive_years": 10,
#   "growth_years": 8,
#   "avg_growth_rate": 0.07,
#   "is_aristocrat": false,  # 25+ years
#   "meets_5year_criteria": true
# }
```

#### 4. **Industry/Sector P/E Comparison** - Hard to Add
```python
# Requirement: P/E < Industry Average
# Currently have: Individual stock P/E
# Missing: Industry/sector average P/E

# Options:
# 1. Fetch from API (if available in Polygon/Alpha Vantage)
# 2. Calculate manually from industry peers
# 3. Use hardcoded industry benchmarks
# 4. Skip for MVP - user can manually compare

# Action: Research API endpoints for sector/industry metrics
```

#### 5. **Piotroski F-Score** - Moderate to Add (Bonus Metric)
```python
# All 9 components calculable from existing data:
✅ 1. Net Income > 0
✅ 2. Operating Cash Flow > 0
✅ 3. ROA change (positive)
✅ 4. Quality of Earnings (OCF > Net Income)
✅ 5. Long-term Debt / Assets change (decreasing)
✅ 6. Current Ratio change (increasing)
✅ 7. No new shares issued
✅ 8. Gross Margin change (increasing)
✅ 9. Asset Turnover change (increasing)

# Action: Create PiotroskiFScoreCalculator (all data available!)
```

---

## 2. MOMENTUM TRADING SCREENER - Data Availability

### ✅ AVAILABLE (1/10 metrics)

| Metric | Status | Implementation |
|--------|--------|----------------|
| **Beta** | ⚠️ Config Only | Defined in config but NOT implemented in calculators |

### ❌ MISSING (9/10 metrics)

#### 1. **RSI (Relative Strength Index)** - Hard to Add
```python
# Requirement: RSI 50-70
# Formula: RSI = 100 - (100 / (1 + RS))
#          RS = Average Gain / Average Loss over 14 periods

# Missing Data:
❌ Historical daily/hourly price data (need 14+ periods minimum)
❌ Current API only provides single-day price (open/high/low/close)

# Required API Call:
- Need: /v2/aggs/ticker/{ticker}/range/{timespan}/{from}/{to}
- Example: Last 30 days of daily data
- Polygon.io supports this endpoint ✅

# Action:
1. Add historical price fetching to DataFetcher
2. Create RSICalculator with 14-period default
```

#### 2. **Price Rate of Change (ROC)** - Hard to Add
```python
# Requirement: Positive ROC over 1-week, 1-month, 3-month
# Formula: ROC = ((Price_current - Price_n_periods_ago) / Price_n_periods_ago) * 100

# Missing Data:
❌ Historical price data (1-week, 1-month, 3-month ago)

# Required: Same as RSI - historical price series

# Action:
1. Use historical price data from #1
2. Create ROCCalculator (multi-timeframe)
```

#### 3. **MACD (Moving Average Convergence/Divergence)** - Hard to Add
```python
# Requirement: MACD line crossing above signal line
# Formula:
#   MACD Line = 12-day EMA - 26-day EMA
#   Signal Line = 9-day EMA of MACD Line
#   Histogram = MACD Line - Signal Line

# Missing Data:
❌ Historical price data (need 26+ days minimum)

# Action:
1. Use historical price data from #1
2. Create MACDCalculator with standard 12/26/9 periods
```

#### 4. **Moving Averages (20-day, 50-day, 200-day)** - Hard to Add
```python
# Requirement: Price > 20-MA > 50-MA > 200-MA
# Formula: SMA = Sum of closing prices / N periods

# Missing Data:
❌ Historical price data (need 200+ days)

# Action:
1. Use historical price data from #1
2. Create MovingAverageCalculator
3. Check golden alignment condition
```

#### 5. **Volume Data & Volume Surge** - Moderate to Add
```python
# Requirement: Current volume > 1.5x average 20-day volume
# Missing Data:
❌ Current day volume
❌ Historical volume data (20+ days)

# Polygon.io provides volume in aggregates:
✅ /v2/aggs/ticker/{ticker}/prev - has volume field
✅ /v2/aggs/ticker/{ticker}/range - has volume per period

# Action:
1. Add volume field to price data model
2. Fetch historical volume with price data
3. Create VolumeAnalysisCalculator
```

#### 6. **52-Week High/Low** - Moderate to Add
```python
# Requirement: Trading within 15-20% of 52-week high

# Missing Data:
❌ 52-week high price
❌ 52-week low price

# Options:
# 1. Calculate from 252 days of historical data
# 2. Yahoo Finance provides this directly in .info
✅ yfinance ticker.info has 'fiftyTwoWeekHigh' and 'fiftyTwoWeekLow'

# Action:
1. Add to YahooFinanceAdapter in market_data mapping
2. Create FiftyTwoWeekAnalysisCalculator
```

#### 7. **Average Daily Volume** - Moderate to Add
```python
# Requirement: Minimum 500K shares/day

# Missing Data:
❌ Average daily volume

# Yahoo Finance provides:
✅ ticker.info['averageVolume'] (3-month avg)
✅ ticker.info['averageVolume10days'] (10-day avg)

# Action:
1. Add to YahooFinanceAdapter market_data
2. Add filter in screener logic
```

#### 8. **Beta (Volatility)** - Moderate to Add
```python
# Requirement: Beta > 1.2

# Current Status:
⚠️ Defined in default_assumptions.json but NOT calculated

# Yahoo Finance provides:
✅ ticker.info['beta']

# Action:
1. Add beta to YahooFinanceAdapter market_data extraction
2. Create BetaCalculator (or just use direct value)
3. Validate against market index (S&P 500)
```

#### 9. **Earnings Momentum** - Moderate to Add
```python
# Requirement: Positive earnings surprises in last 2 quarters

# Missing Data:
❌ Analyst estimates
❌ Actual reported earnings
❌ Earnings surprise percentage

# Yahoo Finance may have:
- ticker.earnings_dates (with estimates and actuals)
- ticker.info['earningsSurprise'] (if available)

# Alternative APIs:
- Alpha Vantage: EARNINGS endpoint
- Polygon.io: May have earnings calendar

# Action:
1. Research API endpoints for earnings data
2. Create EarningsSurpriseCalculator
```

#### 10. **Institutional Ownership Changes** - Very Hard to Add
```python
# Requirement: Increasing institutional ownership in last quarter

# Missing Data:
❌ Institutional ownership percentage
❌ Historical institutional ownership changes
❌ Form 13F filing data

# Potential Sources:
- SEC EDGAR API (13F filings) - Complex to parse
- Yahoo Finance: ticker.institutional_holders
- Alpha Vantage: May not have this
- Polygon.io: Premium tier may have

# Action:
1. Research data availability
2. May need premium data source
3. Consider as "Phase 2" feature
```

---

## 3. TECHNICAL INDICATORS LIBRARY OPTION

### Use Existing Library Instead of Building From Scratch

Rather than implementing technical indicators manually, we can use **TA-Lib** or **pandas-ta**:

#### Option A: TA-Lib (Industry Standard)
```bash
pip install TA-Lib
```

```python
import talib

# RSI
rsi = talib.RSI(prices, timeperiod=14)

# MACD
macd, signal, hist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)

# Moving Averages
sma20 = talib.SMA(prices, timeperiod=20)
sma50 = talib.SMA(prices, timeperiod=50)
sma200 = talib.SMA(prices, timeperiod=200)

# 50+ more indicators available
```

#### Option B: pandas-ta (Pure Python)
```bash
pip install pandas-ta
```

```python
import pandas_ta as ta

df['RSI'] = ta.rsi(df['close'], length=14)
df['MACD'] = ta.macd(df['close'])
df['SMA_20'] = ta.sma(df['close'], length=20)
```

**Recommendation**: Use pandas-ta for easier integration with existing pandas workflows.

---

## 4. PRIORITY ACTION ITEMS

### Phase 1: Complete Value Screener (1-2 days)

| Priority | Metric | Difficulty | Time Estimate |
|----------|--------|------------|---------------|
| 🔴 HIGH | Current Ratio Calculator | Easy | 30 mins |
| 🔴 HIGH | Earnings Stability Counter | Easy | 1 hour |
| 🟡 MEDIUM | Dividend History Analyzer | Moderate | 2 hours |
| 🟢 LOW | Piotroski F-Score | Moderate | 3 hours |
| 🟢 LOW | Industry P/E Comparison | Hard | Research needed |

**Deliverable**: Fully functional value investing screener

---

### Phase 2: Add Basic Momentum Data (2-3 days)

| Priority | Component | Difficulty | Time Estimate |
|----------|-----------|------------|---------------|
| 🔴 HIGH | Historical Price Data Fetcher | Moderate | 3 hours |
| 🔴 HIGH | Install pandas-ta library | Easy | 15 mins |
| 🟡 MEDIUM | Volume Data Integration | Moderate | 2 hours |
| 🟡 MEDIUM | 52-Week High/Low | Easy | 1 hour |
| 🟡 MEDIUM | Beta Implementation | Easy | 1 hour |
| 🟡 MEDIUM | Average Volume | Easy | 30 mins |

**Deliverable**: Price and volume data infrastructure

---

### Phase 3: Technical Indicators (2-3 days)

| Priority | Indicator | Difficulty | Time Estimate |
|----------|-----------|------------|---------------|
| 🔴 HIGH | RSI Calculator | Easy* | 1 hour |
| 🔴 HIGH | Moving Averages (20/50/200) | Easy* | 1 hour |
| 🔴 HIGH | MACD Calculator | Easy* | 1 hour |
| 🟡 MEDIUM | ROC (Multi-timeframe) | Easy* | 1 hour |
| 🟡 MEDIUM | Volume Analysis | Moderate | 2 hours |

*Easy with pandas-ta library

**Deliverable**: Core momentum indicators

---

### Phase 4: Advanced Momentum Features (3-5 days)

| Priority | Feature | Difficulty | Time Estimate |
|----------|---------|------------|---------------|
| 🟡 MEDIUM | Earnings Surprise Data | Hard | 4 hours |
| 🟢 LOW | Institutional Ownership | Very Hard | Research + 8 hours |

**Deliverable**: Complete momentum screener

---

## 5. DATA FETCHING CHANGES REQUIRED

### New API Endpoints to Implement

#### A. Polygon.io - Historical Price Data
```python
# Add to PolygonAdapter class
def fetch_historical_prices(self, ticker: str, from_date: str, to_date: str, timespan: str = 'day'):
    """
    Endpoint: /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
    Returns: List of OHLCV bars with volume
    """
    pass
```

#### B. Yahoo Finance - Market Data Enhancements
```python
# Add to YahooFinanceAdapter market_data extraction
{
    "beta": info.get("beta"),
    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
    "average_volume": info.get("averageVolume"),
    "average_volume_10day": info.get("averageVolume10days"),
}
```

#### C. Volume Data in Current Price Fetcher
```python
# Update PolygonAdapter.fetch_current_price()
# Already returns volume in 'v' field - just need to map it
{
    "price": {
        "open": results["o"],
        "high": results["h"],
        "low": results["l"],
        "close": results["c"],
        "volume": results["v"],  # ADD THIS
    }
}
```

---

## 6. NEW METRIC CALCULATORS TO CREATE

### Value Investing (Missing 3)

1. **`CurrentRatioCalculator`**
   - Path: `core/metrics/calculators/current_ratio.py`
   - Category: Financial Strength

2. **`EarningsStabilityCalculator`**
   - Path: `core/metrics/calculators/earnings_stability.py`
   - Category: Profitability

3. **`DividendHistoryCalculator`**
   - Path: `core/metrics/calculators/dividend_history.py`
   - Category: Capital Allocation

### Momentum Trading (Missing 10)

4. **`RSICalculator`** (via pandas-ta)
5. **`MACDCalculator`** (via pandas-ta)
6. **`MovingAverageCalculator`** (via pandas-ta)
7. **`ROCCalculator`** (via pandas-ta)
8. **`VolumeAnalysisCalculator`**
9. **`FiftyTwoWeekAnalysisCalculator`**
10. **`BetaCalculator`**
11. **`EarningsSurpriseCalculator`**
12. **`InstitutionalOwnershipCalculator`**

### Bonus Calculators

13. **`PiotroskiFScoreCalculator`** (All data available!)

---

## 7. CONFIGURATION UPDATES NEEDED

### Update `metric_profiles.json`

```json
{
  "value_screener": {
    "description": "Metrics for value investing stock screener",
    "metrics": [
      "pe_ratio",
      "pb_ratio",
      "peg_ratio",
      "fcf_yield",
      "roe",
      "debt_to_equity",
      "current_ratio",           // NEW
      "dividend_yield",
      "dividend_history",         // NEW
      "operating_margin",
      "earnings_stability",       // NEW
      "piotroski_fscore"          // NEW (bonus)
    ]
  },
  "momentum_screener": {
    "description": "Metrics for momentum trading stock screener",
    "metrics": [
      "rsi",                      // NEW
      "macd",                     // NEW
      "moving_averages",          // NEW
      "roc",                      // NEW
      "volume_analysis",          // NEW
      "fifty_two_week_analysis",  // NEW
      "beta",                     // NEW
      "earnings_surprise",        // NEW
      "institutional_ownership"   // NEW
    ]
  }
}
```

---

## 8. ESTIMATED TOTAL EFFORT

### Value Screener Completion
- **Time**: 1-2 days
- **Complexity**: Low-Medium
- **Dependencies**: None (all data available)
- **Confidence**: High ✅

### Momentum Screener Completion
- **Time**: 7-10 days
- **Complexity**: Medium-High
- **Dependencies**:
  - Historical price API integration
  - pandas-ta library
  - Possible premium data sources
- **Confidence**: Medium ⚠️

---

## 9. RECOMMENDED APPROACH

### Step 1: Quick Win - Complete Value Screener
1. Add 3 missing calculators (6 hours)
2. Add Piotroski F-Score (3 hours)
3. Test with sample stocks (2 hours)
4. **Total: ~1.5 days**

### Step 2: Data Infrastructure for Momentum
1. Add historical price fetching (3 hours)
2. Install and test pandas-ta (1 hour)
3. Update data models for volume (2 hours)
4. **Total: ~1 day**

### Step 3: Core Technical Indicators
1. Implement RSI, MACD, MAs (3 hours with library)
2. Add 52-week high/low, beta (2 hours)
3. Volume analysis (2 hours)
4. **Total: ~1 day**

### Step 4: Advanced Features
1. ROC multi-timeframe (1 hour)
2. Earnings surprise (4 hours + research)
3. Institutional ownership (research + defer?)
4. **Total: ~1-2 days**

---

## GRAND TOTAL: 5-7 days for both screeners

**Value Screener**: Ready in 1.5 days ✅
**Momentum Screener**: Ready in 5.5 days ⚠️
