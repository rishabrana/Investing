# Investment Analysis Web Application - Technical Specification

**Version:** 1.0
**Date:** October 14, 2025
**Status:** Pending Review

---

## Executive Summary

A responsive React-based web application for stock analysis, providing real-time access to Buffett-style investment metrics. The system leverages existing CLI infrastructure through a REST API server, ensuring consistency between web and command-line interfaces.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Web Application                    │
│  ┌──────────────┐              ┌────────────────────────┐  │
│  │   Sidebar    │              │    Main Content Area   │  │
│  │  (Watchlist) │              │   (Metrics & Charts)   │  │
│  └──────────────┘              └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ REST API (JSON)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Web Server                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           API Endpoints (CRUD + Analytics)          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Shared Business Logic
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Existing Core Services (Python)                 │
│  • JsonStore                 • MetricsService               │
│  • DataIngestionService      • MetricCalculator             │
│  • DataSourceRouter          • Watchlist Management         │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Specification

### Technology Stack

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts or Chart.js
- **State Management**: React Query + Zustand
- **HTTP Client**: Axios
- **Responsive Design**: Mobile-first approach (320px → 2560px)

### Layout Structure

#### Desktop Layout (≥1024px)
```
┌──────────────────────────────────────────────────────────────┐
│                        Header/Nav Bar                         │
│                   (Logo, Settings, Profile)                   │
├──────────┬───────────────────────────────────────────────────┤
│          │                                                    │
│  Watch-  │              Selected Stock Analysis              │
│  list    │                                                    │
│  Panel   │  ┌─────────────────────────────────────────────┐ │
│          │  │  Stock Header (Ticker, Name, Price, +/-)    │ │
│  (280px) │  └─────────────────────────────────────────────┘ │
│          │                                                    │
│  • AAPL  │  [Valuation] [Profitability] [Cash] [Strength]  │
│  • MSFT  │  ┌──────────────┬──────────────┐                │
│  • GOOGL │  │  Metric Cards │  Time Series │                │
│  + Add   │  │              │    Charts    │                │
│          │  └──────────────┴──────────────┘                │
│          │                                                    │
└──────────┴───────────────────────────────────────────────────┘
```

#### Mobile Layout (<1024px)
```
┌──────────────────────────────┐
│      Header (Hamburger)      │
├──────────────────────────────┤
│  ▼ Watchlist Dropdown        │
│    • AAPL (selected)         │
│    • MSFT                    │
│    • GOOGL                   │
│    + Add New                 │
├──────────────────────────────┤
│   Stock: AAPL - $247.66     │
│   Apple Inc.  ▲ +2.3%       │
├──────────────────────────────┤
│  [Tabs: Val|Prof|Cash|...]  │
│                              │
│  ┌────────────────────────┐ │
│  │   Metric Cards         │ │
│  │   (Stacked)            │ │
│  └────────────────────────┘ │
│                              │
│  ┌────────────────────────┐ │
│  │   Chart (Full Width)   │ │
│  └────────────────────────┘ │
└──────────────────────────────┘
```

---

## Data Groupings & Categories

Based on the existing `metric_catalog.yaml` and calculated metrics:

### 1. **Valuation** (How expensive is it?)
```
┌─────────────────────────────────────────┐
│ Price to Earnings (P/E)      39.21     │
│ Price to Book (P/B)          64.54     │
│ EV/EBITDA                    27.79     │
│ PEG Ratio                    141.27    │
│ Margin of Safety             -45%      │
└─────────────────────────────────────────┘
```
**Chart**: Historical P/E and P/B trends (5 years)

### 2. **Profitability** (How profitable is the business?)
```
┌─────────────────────────────────────────┐
│ Return on Equity (ROE)       164.6%    │
│ Return on Invested Capital    75.6%    │
│ Operating Margin             31.5%     │
│ Net Margin                   24.0%     │
│ 10-Year Avg ROCE             39.6%     │
└─────────────────────────────────────────┘
```
**Chart**: ROE, ROIC, and Operating Margin trends (10 years)

### 3. **Growth** (Is it growing?)
```
┌─────────────────────────────────────────┐
│ EPS Growth (CAGR)            0.28%     │
│ Book Value Growth           -0.31%     │
│ Revenue CAGR (5yr)           0.22%     │
└─────────────────────────────────────────┘
```
**Chart**: Revenue, EPS, and Book Value growth lines (10 years)

### 4. **Cash Generation** (Cash flow quality)
```
┌─────────────────────────────────────────┐
│ Free Cash Flow              $127.7B    │
│ Owner Earnings              $114.6B    │
│ Operating Cash Flow         $118.3B    │
│ CapEx Ratio                  7.99%     │
└─────────────────────────────────────────┘
```
**Chart**: FCF vs Net Income vs Owner Earnings (10 years)

### 5. **Financial Strength** (Balance sheet health)
```
┌─────────────────────────────────────────┐
│ Debt to Equity               5.41      │
│ Interest Coverage            N/A       │
│ Current Ratio                0.87      │
│ Cash & Equivalents          $29.9B     │
└─────────────────────────────────────────┘
```
**Chart**: Debt/Equity ratio trend (10 years)

### 6. **Capital Allocation** (How does management deploy capital?)
```
┌─────────────────────────────────────────┐
│ Dividend Yield               0.41%     │
│ Payout Ratio                16.25%     │
│ WACC vs ROIC Spread         67.6%     │
│ Return on Retained Earnings  TBD       │
└─────────────────────────────────────────┘
```
**Chart**: Dividends Paid + Buybacks (annual bars)

### 7. **Competitive Moat** (Durability & consistency)
```
┌─────────────────────────────────────────┐
│ Economic Moat Score         None       │
│   • Margin Stability        92.8%      │
│   • ROIC Trend              Flat       │
│   • Revenue CAGR            0.22%      │
│                                         │
│ Consistency Score           22.7%      │
│   (Low = More Volatile)                │
└─────────────────────────────────────────┘
```
**Chart**: Gross margin stability over 10 years

---

## API Specification

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
- Initial version: No auth (localhost only)
- Future: API key or JWT tokens

### Endpoints

#### Watchlist Management

**GET /watchlist**
```json
// Response
{
  "name": "default",
  "default_metrics_profile": "buffett_core",
  "tickers": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "notes": "Great business, expensive valuation",
      "metrics_profile": null
    }
  ],
  "total_count": 2
}
```

**POST /watchlist/add**
```json
// Request
{
  "symbol": "AAPL",
  "name": "Apple Inc.",  // optional
  "notes": "...",        // optional
  "skip_validation": false
}

// Response
{
  "success": true,
  "message": "Added AAPL to watchlist",
  "entry": { "symbol": "AAPL", "name": "Apple Inc." }
}
```

**DELETE /watchlist/{symbol}**
```json
// Response
{
  "success": true,
  "message": "Removed AAPL from watchlist"
}
```

**POST /watchlist/validate**
```json
// Request
{ "symbol": "AAPL" }

// Response
{
  "is_valid": true,
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "error": null
}
```

#### Stock Data & Metrics

**GET /stocks/{ticker}/overview**
```json
// Response
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "price": {
    "close": 247.66,
    "change": 2.10,
    "change_percent": 0.85,
    "as_of": "2025-10-14"
  },
  "market_data": {
    "market_cap": 3675370987400,
    "shares_outstanding": 14840390000
  }
}
```

**GET /stocks/{ticker}/metrics**
```json
// Query params: ?profile=buffett_core
// Response
{
  "ticker": "AAPL",
  "as_of": "2025-10-14",
  "calculated_at": "2025-10-14T23:18:58",
  "profile_used": "buffett_core",
  "valuation": {
    "price_to_earnings": 39.21,
    "price_to_book": 64.54,
    "ev_to_ebitda": 27.79,
    "peg_ratio": 141.27
  },
  "profitability": {
    "return_on_invested_capital": 0.7563,
    "return_on_equity": 1.6459,
    "operating_and_net_margin": {
      "operating_margin": 0.3151,
      "net_margin": 0.2397
    },
    "eps_growth": 0.0028,
    "book_value_per_share_growth": -0.0031,
    "ten_year_average_roce": 0.3962
  },
  "cash_generation": {
    "free_cash_flow": 127701000000.0,
    "owner_earnings": 114628000000.0,
    "capital_expenditure_ratio": 0.0799
  },
  "financial_strength": {
    "debt_to_equity_and_interest_coverage": {
      "debt_to_equity": 5.4088,
      "interest_coverage": null
    }
  },
  "capital_allocation": {
    "dividend_yield_and_payout_ratio": {
      "dividend_yield": 0.0041,
      "payout_ratio": 0.1625
    },
    "wacc_vs_roic_spread": 0.6763
  },
  "moat": {
    "economic_moat_score": {
      "score": 0.2792,
      "label": "none",
      "margin_stability": 0.9277,
      "roic_trend": 0,
      "revenue_cagr": 0.0022
    },
    "consistency_score": {
      "score": 0.2272,
      "label": "low"
    }
  }
}
```

**GET /stocks/{ticker}/history**
```json
// Query params: ?metric=roic&years=10
// Response
{
  "ticker": "AAPL",
  "metric": "return_on_invested_capital",
  "data_points": [
    { "period": "2014-09-28", "value": 0.42 },
    { "period": "2015-09-27", "value": 0.38 },
    { "period": "2016-09-25", "value": 0.35 },
    { "period": "2017-10-01", "value": 0.31 },
    { "period": "2018-09-30", "value": 0.28 },
    { "period": "2019-09-29", "value": 0.33 },
    { "period": "2020-09-27", "value": 0.41 },
    { "period": "2021-09-26", "value": 0.52 },
    { "period": "2022-09-25", "value": 0.61 },
    { "period": "2023-10-01", "value": 0.76 }
  ]
}
```

**POST /stocks/{ticker}/refresh**
```json
// Request body (optional)
{
  "force": true  // bypass cache
}

// Response
{
  "success": true,
  "ticker": "AAPL",
  "fields_fetched": 27,
  "fields_missing": 0,
  "timestamp": "2025-10-14T21:05:00",
  "providers_used": {
    "polygon.io": 1,
    "alpha_vantage": 4
  }
}
```

#### Batch Operations

**POST /stocks/refresh-watchlist**
```json
// Request
{
  "watchlist": "default",  // optional
  "force": false
}

// Response
{
  "success": true,
  "processed": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "ticker": "AAPL",
      "success": true,
      "fields_fetched": 27
    },
    {
      "ticker": "MSFT",
      "success": true,
      "fields_fetched": 27
    }
  ]
}
```

---

## Backend Specification

### Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **ASGI Server**: Uvicorn
- **CORS**: Enabled for localhost:3000 (React dev server)
- **Dependency Injection**: Use existing services
- **Validation**: Pydantic models

### Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── dependencies.py      # DI for JsonStore, services
│   └── routes/
│       ├── __init__.py
│       ├── watchlist.py     # Watchlist CRUD endpoints
│       ├── stocks.py        # Stock data & metrics endpoints
│       └── health.py        # Health check endpoint
├── models/
│   ├── __init__.py
│   ├── requests.py          # Pydantic request models
│   └── responses.py         # Pydantic response models
└── requirements.txt
```

### Shared Business Logic Integration

The API server will directly import and use existing services:

```python
# api/dependencies.py
from storage.json_store import JsonStore
from services.data_ingestion_service import DataIngestionService
from services.metrics_service import MetricsService

def get_json_store() -> JsonStore:
    """Dependency injection for JsonStore."""
    return JsonStore(data_dir="./data")

def get_data_ingestion_service(
    store: JsonStore = Depends(get_json_store)
) -> DataIngestionService:
    """Dependency injection for DataIngestionService."""
    return DataIngestionService(json_store=store)

def get_metrics_service(
    store: JsonStore = Depends(get_json_store)
) -> MetricsService:
    """Dependency injection for MetricsService."""
    return MetricsService(json_store=store)
```

This ensures:
- CLI and Web API share the same business logic
- No code duplication
- Consistent behavior across interfaces

---

## UI/UX Specifications

### Component Hierarchy

```
App
├── Header
│   ├── Logo
│   ├── RefreshAllButton
│   └── SettingsMenu
├── Layout
│   ├── Sidebar (Desktop) / Dropdown (Mobile)
│   │   ├── WatchlistHeader
│   │   ├── WatchlistItem[]
│   │   │   ├── TickerSymbol
│   │   │   ├── CompanyName
│   │   │   └── RemoveButton
│   │   └── AddTickerButton
│   └── MainContent
│       ├── StockHeader
│       │   ├── TickerInfo (Symbol, Name)
│       │   ├── PriceDisplay (Price, Change)
│       │   └── RefreshButton
│       ├── MetricTabs (Mobile) / CategoryNav (Desktop)
│       └── MetricSection[]
│           ├── SectionHeader
│           ├── MetricCards[]
│           │   ├── MetricLabel
│           │   ├── MetricValue
│           │   ├── MetricChange (optional)
│           │   └── InfoTooltip
│           └── MetricChart
└── Modal
    └── AddTickerForm
        ├── TickerInput (with validation)
        ├── CompanyNameDisplay
        ├── NotesTextarea (optional)
        └── SubmitButton
```

### Color Scheme & Visual Design

**Color Palette** (Buffett-inspired: Classic, professional)
```css
--primary:       #1E40AF  /* Deep Blue */
--secondary:     #059669  /* Green - for positive */
--danger:        #DC2626  /* Red - for negative */
--neutral:       #64748B  /* Slate Gray */
--background:    #F8FAFC  /* Light Gray */
--card-bg:       #FFFFFF  /* White */
--border:        #E2E8F0  /* Light Border */
--text-primary:  #0F172A  /* Dark */
--text-secondary:#64748B  /* Gray */
```

**Typography**
- Headers: Inter or SF Pro (Apple system font)
- Body: system-ui, -apple-system, BlinkMacSystemFont
- Numbers: Tabular figures (font-variant-numeric: tabular-nums)
- Monospace: For ticker symbols

**Metric Card Design**
```
┌─────────────────────────────┐
│ Return on Equity (ROE)   [?]│ ← Tooltip icon
│                             │
│        164.6%               │ ← Large, bold (2xl)
│     ▲ +12.3% YoY            │ ← Small, green/red
│                             │
└─────────────────────────────┘
```

### Responsive Breakpoints

| Breakpoint | Width       | Layout                          |
|------------|-------------|---------------------------------|
| Mobile     | < 768px     | Stacked, hamburger menu         |
| Tablet     | 768-1023px  | Sidebar collapses to drawer     |
| Desktop    | 1024-1439px | Full sidebar + single column    |
| Wide       | ≥ 1440px    | Full sidebar + multi-column     |

### Accessibility

- ARIA labels for all interactive elements
- Keyboard navigation support
- Focus indicators
- Semantic HTML
- Color contrast ratio ≥ 4.5:1

---

## Data Flow

### Initial Page Load
```
1. User opens web app → GET /watchlist
2. Display watchlist in sidebar
3. Auto-select first ticker (e.g., AAPL)
4. Parallel requests:
   - GET /stocks/AAPL/overview
   - GET /stocks/AAPL/metrics
   - GET /stocks/AAPL/history?metric=roic&years=10
   - GET /stocks/AAPL/history?metric=free_cash_flow&years=10
   - ... (one per chart)
5. Render metrics grouped by category with charts
```

### Adding a Ticker
```
1. User clicks "+ Add Ticker" → Opens modal
2. User types "TSLA"
3. Debounced validation → POST /watchlist/validate
4. Display: "Tesla, Inc." with checkmark
5. User clicks "Add to Watchlist"
6. POST /watchlist/add
7. Background: POST /stocks/TSLA/refresh (may take 10-30s)
8. Update sidebar with new ticker
9. Switch to TSLA view
10. Show loading state until refresh completes
```

### Removing a Ticker
```
1. User clicks [X] on MSFT
2. Confirmation dialog: "Remove MSFT from watchlist?"
3. User confirms
4. DELETE /watchlist/MSFT
5. Remove from sidebar
6. Switch to previous/next ticker
```

### Refreshing Data
```
1. User clicks "Refresh" button on AAPL
2. Button shows loading spinner
3. POST /stocks/AAPL/refresh
4. Backend:
   - Calls DataIngestionService.refresh_ticker("AAPL")
   - Calls MetricsService.calculate_metrics("AAPL")
5. Response with updated timestamp
6. Re-fetch: GET /stocks/AAPL/metrics
7. Update all metric cards and charts
8. Show toast: "AAPL data refreshed"
```

### Chart Interaction
```
1. User hovers over chart point
2. Show tooltip with exact value and date
3. User can toggle metrics on/off (multi-line charts)
4. Optional: Click to zoom/pan
```

---

## Key Features

### Must-Have (MVP - Phase 1)
- ✅ Watchlist CRUD (add, remove, list)
- ✅ Display all 7 metric categories
- ✅ Basic line charts for trends (1 per category)
- ✅ Responsive design (mobile + desktop)
- ✅ Refresh button per stock
- ✅ Ticker validation before adding
- ✅ Loading states and error handling

### Nice-to-Have (Phase 2)
- 📊 Advanced charts (candlestick, multi-metric comparison)
- 🔍 Search/filter watchlist
- 💾 Multiple watchlist support
- 📱 PWA (installable on mobile)
- 🌙 Dark mode toggle
- 📈 Side-by-side comparison (AAPL vs MSFT)
- 📧 Email alerts when metrics breach thresholds
- 📝 Notes per ticker
- 🏷️ Tags/categories for stocks
- 📥 Export data (CSV, PDF)

### Future Enhancements (Phase 3+)
- 🔐 User authentication
- ☁️ Cloud sync across devices
- 🤖 AI-powered insights
- 📰 News integration
- 🎯 Custom metric formulas
- 📊 Portfolio tracking
- 🔔 Real-time price alerts

---

## Technical Decisions & Rationale

### Why FastAPI?
- ✅ Native async support for concurrent API calls
- ✅ Automatic OpenAPI/Swagger documentation
- ✅ Pydantic validation (type safety)
- ✅ Fast development with Python
- ✅ Easy integration with existing codebase

### Why React + TypeScript?
- ✅ Component-based architecture (reusable UI)
- ✅ Strong typing prevents runtime errors
- ✅ Large ecosystem of libraries
- ✅ Great developer experience
- ✅ Industry standard for modern web apps

### Why React Query?
- ✅ Automatic caching & refetching
- ✅ Loading/error states out of the box
- ✅ Optimistic updates
- ✅ Background data synchronization
- ✅ Reduces boilerplate code by 80%

### Why Recharts?
- ✅ Built for React (not a wrapper)
- ✅ Responsive by default
- ✅ Composable API (easy to customize)
- ✅ Good TypeScript support
- ✅ Small bundle size

### Why Tailwind CSS?
- ✅ Utility-first (rapid development)
- ✅ No CSS naming conflicts
- ✅ Tree-shaking (small production bundle)
- ✅ Responsive design made easy
- ✅ Consistent design system

---

## Performance Considerations

### Frontend
- Code splitting by route
- Lazy load charts (only render visible ones)
- Memoize expensive calculations
- Virtualize long watchlists (if >100 items)
- Image optimization (if logos added)

### Backend
- Cache API responses (5-15 min TTL)
- Use async/await for parallel data fetching
- Compress responses (gzip)
- Implement rate limiting per client
- Database indexes (if switching from JSON to SQL)

### Network
- HTTP/2 for multiplexing
- Minimize API calls (batch requests)
- WebSocket for real-time updates (future)

---

## Security Considerations

### Phase 1 (MVP - Localhost Only)
- No authentication required
- CORS restricted to localhost:3000
- Input validation via Pydantic
- SQL injection N/A (using JSON files)

### Phase 2 (Production)
- JWT authentication
- API rate limiting (per user)
- HTTPS only
- Secure headers (CSP, HSTS)
- Input sanitization
- API key rotation

---

## Testing Strategy

### Backend Tests
```python
# pytest with FastAPI TestClient
tests/
├── test_watchlist_endpoints.py
├── test_stocks_endpoints.py
└── test_integration.py
```

### Frontend Tests
```typescript
// Vitest + React Testing Library
src/
├── components/
│   └── MetricCard.test.tsx
├── hooks/
│   └── useWatchlist.test.ts
└── utils/
    └── formatters.test.ts
```

### E2E Tests
- Playwright or Cypress
- Test critical user journeys:
  - Add ticker → View metrics → Remove ticker
  - Refresh data → Verify update

---

## Deployment

### Development
```bash
# Backend
cd backend
python -m uvicorn api.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Production (Docker)
```dockerfile
# Multi-stage build
FROM node:18 AS frontend-build
# ... build React app

FROM python:3.11 AS backend
# ... install dependencies
COPY --from=frontend-build /app/dist /app/static
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

---

## Development Plan

### Week 1: Backend Foundation
- [x] Set up FastAPI project structure
- [ ] Implement watchlist endpoints
- [ ] Implement stock data endpoints
- [ ] Add CORS middleware
- [ ] Write API tests
- [ ] Generate OpenAPI docs

### Week 2: Frontend Core
- [ ] Set up React + Vite + TypeScript
- [ ] Configure Tailwind CSS
- [ ] Implement layout (header, sidebar, main)
- [ ] Connect to API with React Query
- [ ] Build watchlist component
- [ ] Build stock header component

### Week 3: Metrics Display
- [ ] Create metric card components
- [ ] Implement 7 category sections
- [ ] Integrate Recharts (basic line charts)
- [ ] Mobile responsive styling
- [ ] Loading states & error handling
- [ ] Add tooltips with metric definitions

### Week 4: Polish & Testing
- [ ] Chart interactivity (hover, zoom)
- [ ] Add refresh functionality
- [ ] Performance optimization
- [ ] Write tests (frontend + backend)
- [ ] Documentation
- [ ] Deployment setup

---

## Open Questions for Review

1. **Metric Groupings**: Do the 7 categories (Valuation, Profitability, Growth, Cash Generation, Financial Strength, Capital Allocation, Competitive Moat) make sense? Any adjustments needed?

2. **Chart Priorities**: Which charts are most important for MVP? Should we implement all 7, or start with 3-4?

3. **Mobile Layout**: Is the collapsible sidebar/dropdown approach acceptable, or do you prefer bottom navigation tabs?

4. **Color Scheme**: Do you like the blue/green/red palette, or do you have brand colors in mind?

5. **Historical Data**: How many years of history should we show by default in charts? (Suggested: 5-10 years)

6. **Metric Definitions**: Should we show tooltips with the `end_user_definition` from metric_catalog.yaml on hover?

7. **Refresh Frequency**: How often should we allow data refreshes? (Suggested: Max 1x per 15 minutes to respect API rate limits)

8. **Default Watchlist**: Should the app create a default watchlist with 2-3 example stocks (AAPL, MSFT) for new users?

9. **Data Persistence**: JSON files are fine for MVP, but should we plan migration to PostgreSQL/SQLite for production?

10. **Real-time Updates**: Do you want live price updates, or is end-of-day data sufficient?

---

## File Structure Preview

```
investing/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── watchlist.py
│   │       ├── stocks.py
│   │       └── health.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py
│   │   └── responses.py
│   ├── tests/
│   │   ├── test_watchlist.py
│   │   └── test_stocks.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── watchlist/
│   │   │   │   ├── WatchlistItem.tsx
│   │   │   │   └── AddTickerModal.tsx
│   │   │   ├── metrics/
│   │   │   │   ├── MetricCard.tsx
│   │   │   │   ├── MetricSection.tsx
│   │   │   │   └── MetricChart.tsx
│   │   │   └── stock/
│   │   │       └── StockHeader.tsx
│   │   ├── hooks/
│   │   │   ├── useWatchlist.ts
│   │   │   ├── useStockMetrics.ts
│   │   │   └── useStockHistory.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   └── formatters.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── data/                    # (Existing)
├── config/                  # (Existing)
├── services/                # (Existing)
├── storage/                 # (Existing)
├── clients/                 # (Existing)
└── docs/
    └── web-app-technical-spec.md  # (This file)
```

---

## Next Steps

1. **Review this specification** and provide feedback
2. **Answer the open questions** above
3. **Approve to proceed** with implementation
4. Start with Week 1 (Backend) or provide adjustments

---

**End of Technical Specification**
