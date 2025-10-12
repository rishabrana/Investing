# Free Stock API Comparison for Missing Data Points

## Executive Summary

Based on comprehensive research, here are the best free API alternatives to supplement Polygon.io for the missing data points in your metric catalog.

---

## 🏆 Recommended Combination

**Primary**: Polygon.io (free tier) - For price data, market data, and basic financials
**Secondary**: Financial Modeling Prep (free tier) OR yfinance - For detailed financial statement fields

---

## Detailed API Comparison

### 1. Financial Modeling Prep (FMP) ⭐ BEST OPTION

**Website**: https://financialmodelingprep.com

#### ✅ Pros
- **Comprehensive coverage**: 25,000+ companies
- **All missing fields available**:
  - ✅ `interestExpense` - Directly available in income statement
  - ✅ `depreciationAndAmortization` - Directly available
  - ✅ `EBITDA` - Directly available
  - ✅ `retainedEarnings` - Available in balance sheet
  - ✅ `operatingIncome` - Directly available
  - ✅ `ebit` - Can be derived or directly available
- **Multiple statement types**: Income, Balance Sheet, Cash Flow, TTM (Trailing Twelve Months)
- **Historical data**: Annual and quarterly statements
- **JSON and CSV formats**
- **Well-documented API**: Clear field names and structure

#### ⚠️ Cons
- Free tier has rate limits (need to verify exact limits)
- Some premium features require paid plans

#### Example Response Structure
```json
{
  "date": "2023-09-30",
  "symbol": "AAPL",
  "revenue": 274515000000,
  "operatingIncome": 66288000000,
  "interestExpense": 2873000000,
  "depreciationAndAmortization": 11056000000,
  "EBITDA": 77344000000,
  "netIncome": 57411000000,
  ...
}
```

#### API Endpoints
```
Income Statement: /api/v3/income-statement/{ticker}?limit=120&apikey={key}
Balance Sheet: /api/v3/balance-sheet-statement/{ticker}?limit=120&apikey={key}
Cash Flow: /api/v3/cash-flow-statement/{ticker}?limit=120&apikey={key}
```

#### Missing Data Points Coverage
| Data Point | Available? | Field Name |
|------------|-----------|------------|
| interest_expense | ✅ Yes | `interestExpense` |
| depreciation_amortization | ✅ Yes | `depreciationAndAmortization` |
| EBITDA | ✅ Yes | `EBITDA` |
| EBIT | ✅ Yes | `operatingIncome` or calculate |
| retained_earnings | ✅ Yes | `retainedEarnings` (balance sheet) |
| pre_tax_income | ✅ Yes | `incomeBeforeTax` |
| other_non_cash_charges | ⚠️ Maybe | Check cash flow details |

---

### 2. yfinance (Yahoo Finance) ⭐ EASIEST TO USE

**Library**: `pip install yfinance`
**Website**: https://pypi.org/project/yfinance/

#### ✅ Pros
- **Completely free**: No API key required
- **No rate limits**: (for reasonable use)
- **Python-native**: Very easy to integrate
- **Comprehensive data**: ~150 financial metrics via `.info`
- **All statements available**:
  - `ticker.financials` / `ticker.income_stmt` - Income statement
  - `ticker.balance_sheet` - Balance sheet
  - `ticker.cashflow` - Cash flow
- **Available fields**:
  - ✅ EBITDA - Directly in `.info` or income statement
  - ✅ Interest Expense - In income statement
  - ✅ Depreciation - In cash flow statement
  - ✅ Operating Income (EBIT) - In income statement
  - ✅ Retained Earnings - In balance sheet

#### ⚠️ Cons
- **Unofficial API**: Yahoo can change it without notice
- **Personal use only**: Not for commercial applications
- **Less reliable**: Can break or have downtime
- **Data quality**: Sometimes incomplete or inconsistent
- **Historical data**: Limited compared to paid services

#### Example Usage
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Get EBITDA and other metrics
ebitda = ticker.info.get('ebitda')

# Get financial statements
income_stmt = ticker.financials  # or ticker.income_stmt
balance_sheet = ticker.balance_sheet
cash_flow = ticker.cashflow

# Access specific fields
interest_expense = income_stmt.loc['Interest Expense']
depreciation = cash_flow.loc['Depreciation']
retained_earnings = balance_sheet.loc['Retained Earnings']
```

#### Missing Data Points Coverage
| Data Point | Available? | Access Method |
|------------|-----------|---------------|
| interest_expense | ✅ Yes | `ticker.financials.loc['Interest Expense']` |
| depreciation_amortization | ✅ Yes | `ticker.cashflow.loc['Depreciation']` |
| EBITDA | ✅ Yes | `ticker.info['ebitda']` |
| EBIT | ✅ Yes | `ticker.financials.loc['Operating Income']` |
| retained_earnings | ✅ Yes | `ticker.balance_sheet.loc['Retained Earnings']` |
| pre_tax_income | ✅ Yes | `ticker.financials.loc['Income Before Tax']` |
| other_non_cash_charges | ⚠️ Maybe | Check cash flow statement rows |

---

### 3. Alpha Vantage

**Website**: https://www.alphavantage.co

#### ✅ Pros
- Free API key available
- Comprehensive financial statements
- EBITDA available in company overview
- Income statements with normalized GAAP/IFRS fields

#### ⚠️ Cons
- **Rate limits**: 5 API calls/minute, 500 daily calls (very restrictive)
- **Limited compared to other free options**
- Field availability less documented than FMP

#### Rate Limits
- Free: 5 calls/min, 500 calls/day
- Paid: 75-1200 calls/min, unlimited daily

#### Missing Data Points Coverage
| Data Point | Available? | Notes |
|------------|-----------|-------|
| EBITDA | ✅ Yes | Company overview endpoint |
| interest_expense | ⚠️ Likely | In income statement, need to verify |
| depreciation_amortization | ⚠️ Likely | In financial statements, need to verify |
| EBIT | ⚠️ Likely | Should be in income statement |
| retained_earnings | ⚠️ Likely | Should be in balance sheet |

---

### 4. Finnhub

**Website**: https://finnhub.io

#### ✅ Pros
- Generous free tier: 60 calls/minute
- 117 fundamental metrics in basic financials endpoint
- EBIT and EBITDA estimates available
- Company fundamentals included

#### ⚠️ Cons
- **"Financials As Reported" is premium only**
- Free tier provides estimates and restated data, not raw line items
- May not have granular detail like individual expense line items
- Only 1 year of historical data per call

#### Missing Data Points Coverage
| Data Point | Available? | Notes |
|------------|-----------|-------|
| EBITDA | ✅ Yes | EBITDA estimates endpoint |
| EBIT | ✅ Yes | EBIT estimates endpoint |
| interest_expense | ❌ No | Premium tier only (as-reported financials) |
| depreciation_amortization | ❌ No | Premium tier only |
| retained_earnings | ⚠️ Maybe | Check basic financials (117 metrics) |

---

## 📊 Side-by-Side Comparison

| Feature | Polygon.io | FMP | yfinance | Alpha Vantage | Finnhub |
|---------|-----------|-----|----------|---------------|---------|
| **Rate Limit (Free)** | 5/min | ~250/day* | None** | 5/min, 500/day | 60/min |
| **Interest Expense** | ❌ | ✅ | ✅ | ⚠️ | ❌ |
| **Depreciation** | ❌ | ✅ | ✅ | ⚠️ | ❌ |
| **EBITDA** | ❌ | ✅ | ✅ | ✅ | ✅ (estimates) |
| **EBIT** | ⚠️ | ✅ | ✅ | ⚠️ | ✅ (estimates) |
| **Retained Earnings** | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| **Historical Data** | 2 years | 10+ years | ~5 years | ~20 years | 1 year/call |
| **Documentation** | Excellent | Excellent | Good | Good | Good |
| **Reliability** | High | High | Medium | High | High |
| **API Key Required** | Yes | Yes | No | Yes | Yes |
| **Commercial Use** | No (free) | Check terms | No | Check terms | Check terms |

\* FMP free tier limits need verification
\** yfinance has no official limits but should be used reasonably

---

## 🎯 Recommended Implementation Strategy

### Strategy 1: Polygon.io + Financial Modeling Prep (BEST)

**Use Polygon.io for**:
- Price data (OHLC)
- Market cap, shares outstanding
- Basic balance sheet and income statement

**Use FMP for**:
- Interest expense
- Depreciation & amortization
- EBITDA (pre-calculated)
- Retained earnings
- Any other missing calculated fields

**Benefits**:
- Both are official, well-documented APIs
- Better reliability than yfinance
- Clear field names and structure
- Good for production use

**Drawbacks**:
- Need to manage two API keys
- Combined rate limits might be tight
- More complex integration

---

### Strategy 2: Polygon.io + yfinance (EASIEST)

**Use Polygon.io for**:
- Price data
- Market cap, shares outstanding
- Primary financial data source

**Use yfinance as fallback for**:
- Missing fields (interest, depreciation, etc.)
- Quick prototyping
- Gap filling

**Benefits**:
- yfinance is trivial to implement
- No additional API key needed
- Very fast to prototype

**Drawbacks**:
- yfinance is unofficial and can break
- Not suitable for production/commercial use
- Data quality inconsistencies

---

### Strategy 3: yfinance Only (SIMPLEST)

**Use yfinance for everything**

**Benefits**:
- Single data source
- No API keys to manage
- No rate limits
- Easiest implementation
- Has ALL the fields you need

**Drawbacks**:
- Unofficial API
- Can break at any time
- Not for commercial use
- Less reliable than official APIs

---

## 💡 Final Recommendation

### For Development/Learning: **yfinance Only**
Start with yfinance for rapid prototyping. It has everything you need and is dead simple.

```python
import yfinance as yf
ticker = yf.Ticker("AAPL")
# Everything you need is here
```

### For Production: **Polygon.io + FMP**
Use both official APIs for reliability and completeness.

```python
# Price and market data from Polygon
polygon_data = fetch_polygon_data(ticker)

# Missing financial fields from FMP
fmp_data = fetch_fmp_financials(ticker)

# Combine them
complete_data = merge_data(polygon_data, fmp_data)
```

### Hybrid Approach: **Polygon.io + yfinance fallback**
Use Polygon as primary, yfinance for missing fields only.

```python
# Try Polygon first
data = fetch_polygon_data(ticker)

# Fill gaps with yfinance
if data.missing_fields():
    yf_data = fetch_yfinance_data(ticker)
    data.fill_from(yf_data)
```

---

## 🔍 Verification Steps

Before committing to an API, test these:

### For FMP:
- [ ] Sign up and get free API key
- [ ] Test income statement endpoint for interest expense
- [ ] Test balance sheet for retained earnings
- [ ] Verify depreciation in income/cash flow
- [ ] Check rate limits and daily quotas
- [ ] Test historical data retrieval (10 years)

### For yfinance:
- [ ] Install: `pip install yfinance`
- [ ] Test: `yf.Ticker("AAPL").financials`
- [ ] Verify interest expense field exists
- [ ] Check depreciation in cash flow
- [ ] Test retained earnings in balance sheet
- [ ] Verify EBITDA availability
- [ ] Check data quality vs official sources

### For Alpha Vantage:
- [ ] Sign up for free API key
- [ ] Test company overview for EBITDA
- [ ] Check income statement fields
- [ ] Verify rate limits (5/min is very restrictive)
- [ ] Compare data completeness vs FMP/yfinance

---

## 📋 Missing Data Points Summary

Here's what you're missing from Polygon.io and where to get it:

| Data Point | FMP | yfinance | Alpha Vantage | Finnhub | Recommendation |
|------------|-----|----------|---------------|---------|----------------|
| interest_expense | ✅ | ✅ | ⚠️ | ❌ | **FMP or yfinance** |
| depreciation_amortization | ✅ | ✅ | ⚠️ | ❌ | **FMP or yfinance** |
| EBITDA | ✅ | ✅ | ✅ | ✅ | **Any (FMP preferred)** |
| EBIT | ✅ | ✅ | ⚠️ | ✅ | **FMP or yfinance** |
| retained_earnings | ✅ | ✅ | ⚠️ | ⚠️ | **FMP or yfinance** |
| pre_tax_income | ✅ | ✅ | ⚠️ | ⚠️ | **FMP or yfinance** |
| other_non_cash_charges | ⚠️ | ⚠️ | ❌ | ❌ | **Calculate manually** |

---

## 🚀 Quick Start Code Examples

### Option 1: yfinance (Simplest)
```python
import yfinance as yf

def get_missing_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)

    return {
        'interest_expense': ticker.financials.loc['Interest Expense'],
        'depreciation': ticker.cashflow.loc['Depreciation'],
        'ebitda': ticker.info.get('ebitda'),
        'retained_earnings': ticker.balance_sheet.loc['Retained Earnings']
    }

data = get_missing_data("AAPL")
```

### Option 2: Financial Modeling Prep
```python
import requests

def get_fmp_data(ticker, api_key):
    base_url = "https://financialmodelingprep.com/api/v3"

    # Income statement
    income_url = f"{base_url}/income-statement/{ticker}?limit=5&apikey={api_key}"
    income_data = requests.get(income_url).json()

    # Balance sheet
    balance_url = f"{base_url}/balance-sheet-statement/{ticker}?limit=5&apikey={api_key}"
    balance_data = requests.get(balance_url).json()

    return {
        'interest_expense': income_data[0]['interestExpense'],
        'depreciation': income_data[0]['depreciationAndAmortization'],
        'ebitda': income_data[0]['ebitda'],
        'retained_earnings': balance_data[0]['retainedEarnings']
    }

data = get_fmp_data("AAPL", "your_api_key")
```

---

## 💰 Cost Comparison (If You Outgrow Free Tiers)

| Service | Free Tier | Paid Tier | Best For |
|---------|-----------|-----------|----------|
| Polygon.io | 5 calls/min | $29+/mo | Real-time price data |
| FMP | Limited | $15-50/mo | Financial statements |
| Alpha Vantage | 5 calls/min | $50-200/mo | Mixed use |
| yfinance | Free always | N/A | Personal projects |
| Finnhub | 60 calls/min | $50+/mo | Market data focus |

---

## ✅ Conclusion

**Best answer**: Yes, there are several free APIs that can provide the missing data points!

**Quick recommendation**:
1. **For prototyping**: Use yfinance - it has everything you need
2. **For production**: Use FMP alongside Polygon.io for complete coverage
3. **For flexibility**: Start with yfinance, migrate to FMP when ready

All the missing fields (interest expense, depreciation, EBITDA, retained earnings) are readily available in both **Financial Modeling Prep** and **yfinance**.
