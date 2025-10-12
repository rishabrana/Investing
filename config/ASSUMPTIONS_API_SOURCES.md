# Assumptions & Projections - API Data Sources

## Executive Summary

**Good News!** Most "assumptions" can actually be fetched from free APIs! Only a few require true user input.

---

## ✅ API-SOURCED Assumptions (Can be Automated!)

### 1. Beta (Stock Volatility)
**Source**: Financial Modeling Prep (primary), Yahoo Finance (secondary)

```python
# FMP API
GET https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={key}
# Returns: { "beta": 1.23 }

# yfinance
import yfinance as yf
beta = yf.Ticker("AAPL").info['beta']
```

**What it is**: Measures stock's volatility vs market (S&P 500)
- Beta = 1.0 → Stock moves with market
- Beta > 1.0 → More volatile than market
- Beta < 1.0 → Less volatile than market

**Free Tier**: ✅ Yes (FMP: 250 calls/day, yfinance: unlimited)

---

### 2. Risk-Free Rate
**Source**: Alpha Vantage (primary), FMP (secondary)

```python
# Alpha Vantage - 10 Year Treasury Yield
GET https://www.alphavantage.co/query?function=TREASURY_YIELD&maturity=10year&apikey={key}

# Returns latest treasury yield, e.g., 4.06%
```

**What it is**: Return on "risk-free" investment (US 10-Year Treasury Bond)
- Used in CAPM to calculate cost of equity
- Current rate (Oct 2025): ~4.0%

**Free Tier**: ✅ Yes (Alpha Vantage: 5 calls/min, 500/day)

---

### 3. Market Risk Premium
**Source**: Financial Modeling Prep (primary)

```python
# FMP API
GET https://financialmodelingprep.com/api/v3/market-risk-premium?apikey={key}

# Returns historical equity risk premium
```

**What it is**: Additional return expected from stock market vs risk-free rate
- Historical average: ~6%
- Range: 5-7% depending on market conditions

**Free Tier**: ✅ Yes (FMP: 250 calls/day)
**Fallback**: Use default 6.0% if API unavailable

---

### 4. Cost of Equity (CALCULATED)
**Formula**: Risk-Free Rate + (Beta × Market Risk Premium)

```python
cost_of_equity = risk_free_rate + (beta * market_risk_premium)

# Example:
# risk_free_rate = 4.0%
# beta = 1.2
# market_risk_premium = 6.0%
# cost_of_equity = 4.0% + (1.2 × 6.0%) = 11.2%
```

**All inputs**: ✅ Available from APIs!

---

### 5. Cost of Debt (CALCULATED)
**Formula**: Interest Expense / Total Debt

```python
cost_of_debt = interest_expense / total_debt

# After-tax cost of debt
after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
```

**Data Sources**:
- Interest Expense: FMP or Alpha Vantage
- Total Debt: Polygon.io or FMP
- Tax Rate: Calculate from financials

**Free Tier**: ✅ Yes (all components available)

---

### 6. WACC (CALCULATED)
**Formula**: Weighted Average Cost of Capital

```python
equity_value = market_cap
debt_value = total_debt
total_value = equity_value + debt_value

wacc = (equity_value / total_value) * cost_of_equity + \
       (debt_value / total_value) * cost_of_debt * (1 - tax_rate)
```

**All inputs**: ✅ Available from APIs!
- Market cap: Polygon.io
- Total debt: Polygon.io
- Cost of equity: Calculated (see #4)
- Cost of debt: Calculated (see #5)
- Tax rate: Calculated from financials

---

### 7. Projected Free Cash Flows (PARTIALLY API-SOURCED)
**Source**: Financial Modeling Prep (analyst estimates), Finnhub (estimates)

```python
# FMP - Analyst Estimates
GET https://financialmodelingprep.com/api/v3/analyst-estimates/AAPL?apikey={key}

# Returns analyst estimates for:
# - Revenue (next 1-4 quarters/years)
# - EPS (next 1-4 quarters/years)
# - EBITDA estimates
```

**Approach**:
1. Get analyst revenue estimates from API
2. Calculate FCF margin from historical data: `FCF / Revenue`
3. Apply historical FCF margin to projected revenue

```python
# Historical FCF margin (from your data)
fcf_margin = historical_fcf / historical_revenue  # e.g., 0.25 = 25%

# Projected FCF
projected_fcf_year1 = analyst_revenue_estimate_year1 * fcf_margin
projected_fcf_year2 = analyst_revenue_estimate_year2 * fcf_margin
# etc.
```

**Free Tier**: ✅ Partial (analyst estimates for 1-4 years)
**Beyond analyst coverage**: Requires user input or growth assumptions

---

## ⚠️ PARTIAL User Input Required

### 8. Terminal Growth Rate
**Primary**: User input
**Fallback**: GDP growth rate (~2.5%)

**What it is**: Perpetual growth rate after projection period
- Typically: 2-3% (long-term GDP growth)
- Conservative: 2.0%
- Moderate: 2.5%
- Aggressive: 3.0%

**Why user input**: Depends on company maturity, industry, and investor view

**Recommendation**: Use default 2.5%, allow override

---

### 9. Projection Years
**Primary**: User input
**Default**: 10 years

**What it is**: How many years to project cash flows
- Typical range: 5-10 years
- Mature companies: 5 years
- Growth companies: 10 years

**Recommendation**: Default to 10 years, allow override

---

### 10. Discount Rate (Usually WACC)
**Primary**: Calculated WACC (see #6)
**Override**: User can specify custom required return

**What it is**: Rate used to discount future cash flows to present value
- Default: Use WACC
- Alternative: User's personal required rate of return

**Recommendation**: Calculate WACC from APIs, allow user override

---

## 📝 TRUE User Input (No API Source)

### 11. Qualitative Indicators
**Source**: User assessment only

**What it is**: Competitive advantages, moat assessment
- Brand strength
- Network effects
- Cost advantages
- Switching costs
- Regulatory barriers

**Why manual**: Subjective business analysis, no API can provide this

---

## 🎯 Summary Table

| Assumption | API Available? | Primary Source | Free Tier | Fallback |
|------------|----------------|----------------|-----------|----------|
| **Beta** | ✅ Yes | FMP, yfinance | ✅ Yes | Alpha Vantage |
| **Risk-Free Rate** | ✅ Yes | Alpha Vantage | ✅ Yes | Default 4.0% |
| **Market Risk Premium** | ✅ Yes | FMP | ✅ Yes | Default 6.0% |
| **Cost of Equity** | ✅ Calculate | From above APIs | ✅ Yes | N/A |
| **Cost of Debt** | ✅ Calculate | FMP/Polygon | ✅ Yes | Industry avg |
| **WACC** | ✅ Calculate | From above APIs | ✅ Yes | N/A |
| **Analyst Estimates** | ✅ Partial | FMP, Finnhub | ✅ Yes | User input |
| **Projected FCF** | ⚠️ Hybrid | Estimates + calculation | ✅ Partial | User input |
| **Terminal Growth** | ⚠️ Assumption | User input | N/A | Default 2.5% |
| **Projection Years** | ⚠️ Assumption | User input | N/A | Default 10 |
| **Discount Rate** | ✅ Calculate | WACC | ✅ Yes | User override |
| **Qualitative Moat** | ❌ No | User only | N/A | N/A |

---

## 💡 Implementation Recommendations

### Phase 1: Fully Automated WACC Calculation
```python
def calculate_wacc(ticker):
    # All from APIs!
    beta = get_beta(ticker)  # FMP
    risk_free_rate = get_treasury_yield()  # Alpha Vantage
    market_risk_premium = get_market_risk_premium()  # FMP

    cost_of_equity = risk_free_rate + (beta * market_risk_premium)

    # From financials
    interest_expense = get_interest_expense(ticker)  # FMP
    total_debt = get_total_debt(ticker)  # Polygon
    market_cap = get_market_cap(ticker)  # Polygon
    tax_rate = get_effective_tax_rate(ticker)  # Calculated

    cost_of_debt = interest_expense / total_debt

    equity_weight = market_cap / (market_cap + total_debt)
    debt_weight = total_debt / (market_cap + total_debt)

    wacc = (equity_weight * cost_of_equity) + \
           (debt_weight * cost_of_debt * (1 - tax_rate))

    return wacc
```

### Phase 2: Hybrid Projection Model
```python
def generate_projections(ticker, years=10):
    # Get analyst estimates for available years (usually 1-4)
    analyst_estimates = get_analyst_estimates(ticker)  # FMP/Finnhub

    # Calculate historical FCF margin
    historical_data = get_historical_financials(ticker)
    fcf_margin = calculate_avg_fcf_margin(historical_data)

    projections = []

    # Years with analyst coverage: use estimates
    for year in range(1, len(analyst_estimates) + 1):
        estimated_revenue = analyst_estimates[year]['revenue']
        projected_fcf = estimated_revenue * fcf_margin
        projections.append(projected_fcf)

    # Beyond analyst coverage: use growth assumption
    terminal_growth = 0.025  # 2.5% default, allow override
    last_projection = projections[-1]

    for year in range(len(analyst_estimates) + 1, years + 1):
        projected_fcf = last_projection * (1 + terminal_growth)
        projections.append(projected_fcf)
        last_projection = projected_fcf

    return projections
```

### Phase 3: User Override System
```python
class ValuationInputs:
    def __init__(self, ticker):
        self.ticker = ticker

        # Auto-fetch from APIs
        self.beta = self.fetch_beta()
        self.risk_free_rate = self.fetch_risk_free_rate()
        self.market_risk_premium = self.fetch_market_risk_premium()
        self.wacc = self.calculate_wacc()

        # Defaults with override capability
        self.terminal_growth = 0.025  # User can override
        self.projection_years = 10     # User can override
        self.discount_rate = self.wacc  # User can override

    def override_terminal_growth(self, rate):
        """Allow user to override terminal growth rate."""
        self.terminal_growth = rate

    def override_discount_rate(self, rate):
        """Allow user to specify custom discount rate."""
        self.discount_rate = rate
```

---

## 🚀 Quick Start Code

### Fetch All WACC Components
```python
import requests

def get_all_wacc_components(ticker):
    """Fetch all components needed to calculate WACC from free APIs."""

    FMP_KEY = "your_fmp_key"
    AV_KEY = "your_alpha_vantage_key"

    # 1. Beta (FMP)
    profile = requests.get(
        f"https://financialmodelingprep.com/api/v3/profile/{ticker}",
        params={"apikey": FMP_KEY}
    ).json()[0]
    beta = profile['beta']

    # 2. Risk-Free Rate (Alpha Vantage)
    treasury = requests.get(
        f"https://www.alphavantage.co/query",
        params={
            "function": "TREASURY_YIELD",
            "maturity": "10year",
            "apikey": AV_KEY
        }
    ).json()
    risk_free_rate = float(treasury['data'][0]['value']) / 100  # Convert to decimal

    # 3. Market Risk Premium (FMP)
    mrp = requests.get(
        f"https://financialmodelingprep.com/api/v3/market-risk-premium",
        params={"apikey": FMP_KEY}
    ).json()[0]
    market_risk_premium = mrp['marketRiskPremium'] / 100  # Convert to decimal

    # 4. Financial Data (FMP - or use Polygon)
    income = requests.get(
        f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}",
        params={"apikey": FMP_KEY, "limit": 1}
    ).json()[0]

    balance = requests.get(
        f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}",
        params={"apikey": FMP_KEY, "limit": 1}
    ).json()[0]

    interest_expense = income['interestExpense']
    total_debt = balance['totalDebt']
    market_cap = profile['mktCap']
    tax_rate = income['incomeTaxExpense'] / income['incomeBeforeTax']

    return {
        'beta': beta,
        'risk_free_rate': risk_free_rate,
        'market_risk_premium': market_risk_premium,
        'interest_expense': interest_expense,
        'total_debt': total_debt,
        'market_cap': market_cap,
        'tax_rate': tax_rate
    }

# Usage
components = get_all_wacc_components("AAPL")
print(f"Beta: {components['beta']}")
print(f"Risk-Free Rate: {components['risk_free_rate']:.2%}")
print(f"Market Risk Premium: {components['market_risk_premium']:.2%}")
```

---

## 📊 Data Availability Summary

### Fully Available from APIs ✅
- Beta
- Risk-Free Rate (Treasury Yield)
- Market Risk Premium
- Interest Expense
- Total Debt
- Market Cap
- Tax Rate
- Analyst Estimates (1-4 years)

### Requires Calculation (but inputs from APIs) ⚙️
- Cost of Equity (CAPM)
- Cost of Debt
- WACC
- Projected FCF (beyond analyst coverage)

### Requires User Input (with sensible defaults) ⚠️
- Terminal Growth Rate (default: 2.5%)
- Projection Years (default: 10)
- Discount Rate override (default: use WACC)

### Truly Manual 📝
- Qualitative moat indicators
- Custom growth scenarios
- Industry-specific adjustments

---

## 🎯 Bottom Line

**You CAN automate ~90% of DCF valuation assumptions using free APIs!**

Only these require true user decisions:
1. Terminal growth rate (default 2.5% is reasonable)
2. Projection period (default 10 years is standard)
3. Qualitative factors (moat assessment)

Everything else - beta, risk-free rate, market risk premium, WACC - can be fetched automatically from free APIs!
