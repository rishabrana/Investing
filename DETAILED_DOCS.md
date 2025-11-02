# Investing Toolkit Overview

This project provides a comprehensive Python toolkit that helps value-oriented investors retrieve high-quality fundamentals, persist them locally, calculate Buffett-style metrics, and build investment analysis automation. The major components are:

- **JsonStore** (in `storage/json_store.py`): Local JSON-based datastore with strict separation between raw API data and computed metrics, plus watchlist management.
- **DataIngestionService** (in `services/data_ingestion_service.py`): Orchestrates multi-provider data fetching, normalization, and persistence.
- **MetricsService** (in `services/metrics_service.py`): Calculates investment metrics (ROIC, FCF, P/E, etc.) from raw data.
- **Web API & Frontend**: FastAPI backend with React/TypeScript frontend for interactive analysis.
- **CLI Tools**: Command-line interfaces for managing API keys, watchlists, fetching data, and calculating metrics.

The sections below describe how to get started, manage watchlists, fetch data, and calculate metrics.

---

## 1. Quick Start

### Backend Setup

1. **Create / activate the virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start the backend API**
   ```bash
   python3 -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Backend runs at: **http://localhost:8000**

### Frontend Setup

1. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm run dev
   ```
   Frontend runs at: **http://localhost:5173** (or next available port if 5173 is in use)

### Initial Configuration

1. **Create the initial data directory structure**
   - The `JsonStore` automatically creates folders (e.g., `./data/raw`, `./data/watchlists`) the first time you run the CLI or ingestion service.

2. **Provide API keys**
   - Either set environment variables (`POLYGON_API_KEY`, `FMP_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `FINNHUB_API_KEY`), *or*
   - Use the bundled credentials CLI (see §2.1) to store keys securely in `./data/credentials/api_keys.json`, *or*
   - Use the web UI settings menu (gear icon) to add API keys through the browser
   - **Primary provider (required)**: `polygon.io`
   - **Secondary providers (recommended)**: `financial_modeling_prep`, `alpha_vantage`, `finnhub`

---

## 2. Managing Watchlists

Watchlists are persisted inside the `JsonStore` (default location: `./data/watchlists`). Each watchlist file contains the default metrics profile and per-ticker overrides.

### 2.1 Managing API Keys

The toolkit ships with a small CLI for adding, listing, or removing stored API credentials:

```bash
# List currently stored keys (masked)
python -m cli.api_keys_cli list

# Add/update a key
python -m cli.api_keys_cli add polygon.io YOUR_API_KEY

# Remove a key
python -m cli.api_keys_cli remove polygon.io
```

Use `--data-dir` if your JsonStore lives in a custom location.
The CLI will always print the supported provider identifiers and their corresponding environment variables (e.g., `polygon.io`, `financial_modeling_prep`, `alpha_vantage`, `finnhub.io`).

### List existing watchlists

```bash
python -m cli.watchlist_cli list
```

Use `--name` to target a specific watchlist (default is `default`), and `--data-dir` if your data folder is elsewhere:

```bash
python -m cli.watchlist_cli --data-dir ./my_data --name income_funds list
```

### Add a ticker

```bash
python -m cli.watchlist_cli add AAPL --company "Apple Inc" --notes "Consumer tech moat"
```

Optional flags:
- `--profile wide_moat_focus` to set a custom metrics profile for that ticker.
- `--default-profile buffett_core` to update the watchlist’s default profile on save.

### Remove a ticker

```bash
python -m cli.watchlist_cli remove KO
```

### Programmatic access

The `JsonStore` exposes helpers too:

```python
from storage.json_store import JsonStore, load_watchlist_from_store

store = JsonStore()
watchlist = load_watchlist_from_store(store, name="default")
for entry in watchlist.tickers:
    print(entry.symbol, entry.name)
```

---

## 3. Fetching Data with `DataIngestionService`

`DataIngestionService` orchestrates the entire data acquisition workflow:

1. Derives the fields required for each ticker (based on metric catalog).
2. Uses `DataSourceRouter` to minimize API calls across providers (Polygon.io, Alpha Vantage, Yahoo Finance).
3. Normalizes payloads into a standard format.
4. Writes raw snapshots to `JsonStore` (stored in `./data/raw/`).

### 3.1 CLI - Fetch Data

Run the data fetch pipeline from the command line:

```bash
# Fetch data for all tickers in default watchlist
python3 -m cli.data_fetch_cli run

# Use a specific watchlist
python3 -m cli.data_fetch_cli run --watchlist income_funds

# Fetch quarterly data instead of annual
python3 -m cli.data_fetch_cli run --period quarterly

# Resume from previous run (skip already-fetched tickers)
python3 -m cli.data_fetch_cli run --resume

# Limit to first 5 tickers
python3 -m cli.data_fetch_cli run --max-tickers 5

# Don't save historical snapshots (only latest)
python3 -m cli.data_fetch_cli run --no-history
```

**Output Example:**
```json
{
  "timestamp": "2025-10-14T00:19:58.585053",
  "watchlist_size": 2,
  "processed": 2,
  "successful": 2,
  "failed": 0,
  "success_rate": 1.0,
  "providers_used": {
    "polygon.io": 2,
    "alpha_vantage": 2
  },
  "unique_fields_fetched": 23,
  "unique_fields_missing": 3
}
```

### 3.2 Create Sample Watchlist

```bash
# Create a demo watchlist with sample tickers
python3 -m cli.data_fetch_cli create-sample-watchlist --watchlist demo
```

### 3.3 Provider Requirements

Before fetching, the CLI verifies credentials:

- **Primary provider (Polygon.io)**: Required. If no key is found, the command exits with an error.
- **Secondary providers** (`alpha_vantage`, `yahoo_finance`): Optional but recommended for complete data coverage.

The system automatically uses fallback providers when the primary provider doesn't have certain fields (e.g., interest expense, depreciation).

### 3.4 Programmatic Usage

```python
from storage.json_store import JsonStore, load_watchlist_from_store
from services import DataIngestionService, DataSourceRouter, Normalizer
from clients import PolygonClient, AlphaVantageClient, YahooFinanceClient

store = JsonStore()
watchlist = load_watchlist_from_store(store)

# Initialize clients
clients = {
    'polygon.io': PolygonClient(store.get_api_key('polygon.io')),
    'alpha_vantage': AlphaVantageClient(store.get_api_key('alpha_vantage')),
    'yahoo_finance': YahooFinanceClient(),
}

router = DataSourceRouter(clients=clients)
normalizer = Normalizer()

service = DataIngestionService(
    json_store=store,
    data_source_router=router,
    normalizer=normalizer,
    period="annual",
    save_history=True,
)

summary = service.refresh_watchlist(watchlist, resume=False)
print(summary)
```

---

## 4. Calculating Metrics with `MetricsService`

`MetricsService` calculates investment metrics from raw data, following the definitions in `config/metric_catalog.yaml`. Metrics are organized into categories:

- **Valuation**: P/E, P/B, EV/EBITDA
- **Profitability**: ROIC, ROE, Operating/Net Margins
- **Cash Generation**: Free Cash Flow, Owner Earnings, CapEx Ratio
- **Financial Strength**: Debt-to-Equity, Interest Coverage
- **Capital Allocation**: Dividend Yield, Payout Ratio

### 4.1 CLI - Calculate Metrics

**Calculate for a single ticker:**
```bash
# Calculate and show metrics for AAPL
python3 -m cli.metrics_cli calculate AAPL --show

# Calculate without showing (just save)
python3 -m cli.metrics_cli calculate AAPL

# Use a custom metrics profile
python3 -m cli.metrics_cli calculate AAPL --profile wide_moat_focus

# Don't save historical snapshots
python3 -m cli.metrics_cli calculate AAPL --no-history
```

**Calculate for entire watchlist:**
```bash
# Calculate metrics for all tickers in default watchlist
python3 -m cli.metrics_cli calculate-watchlist

# Use a specific watchlist
python3 -m cli.metrics_cli calculate-watchlist --watchlist income_funds

# Limit to first 5 tickers
python3 -m cli.metrics_cli calculate-watchlist --max-tickers 5
```

**Output Example:**
```json
{
  "timestamp": "2025-10-14T00:57:34.051984",
  "watchlist": "default",
  "watchlist_size": 2,
  "processed": 2,
  "successful": 2,
  "failed": 0,
  "success_rate": 1.0,
  "results": [
    {
      "ticker": "AAPL",
      "success": true,
      "metrics_calculated": 11,
      "warnings": 0
    }
  ]
}
```

### 4.2 CLI - View Metrics

**Show latest metrics:**
```bash
# Display calculated metrics for AAPL
python3 -m cli.metrics_cli show AAPL
```

**Output Example:**
```json
{
  "ticker": "AAPL",
  "as_of": "2025-10-14",
  "calculated_at": "2025-10-14T00:57:34.037883",
  "profile": "buffett_core",
  "metrics_count": 11,
  "metrics": {
    "price_to_earnings": 39.21,
    "price_to_book": 64.54,
    "ev_to_ebitda": 27.53,
    "return_on_invested_capital": 0.756,
    "return_on_equity": 1.646,
    "operating_and_net_margin": {
      "operating_margin": 0.315,
      "net_margin": 0.240
    },
    "free_cash_flow": 108807000000.0,
    "owner_earnings": 95734000000.0
  }
}
```

**Show historical metrics:**
```bash
# List all historical metric snapshots
python3 -m cli.metrics_cli history AAPL

# View a specific historical snapshot
python3 -m cli.metrics_cli show AAPL --timestamp 2025-10-14T00-57-34.037883
```

### 4.3 Programmatic Usage

```python
from storage.json_store import JsonStore
from services import MetricsService

store = JsonStore()
service = MetricsService(json_store=store)

# Calculate metrics for a single ticker
snapshot = service.calculate_metrics(
    ticker="AAPL",
    profile="buffett_core",
    save_history=True
)

print(f"Calculated {len(snapshot.metrics_included)} metrics")
print(f"Valuation: {snapshot.valuation}")
print(f"Profitability: {snapshot.profitability}")

# Calculate for entire watchlist
summary = service.calculate_for_watchlist(
    watchlist_name="default",
    save_history=True
)
print(summary)
```

### 4.4 Metrics Calculated

The service currently implements **11 core metrics**:

| Category | Metric | Description |
|----------|--------|-------------|
| **Valuation** | P/E Ratio | Price / Earnings |
| | P/B Ratio | Price / Book Value |
| | EV/EBITDA | Enterprise Value / EBITDA |
| **Profitability** | ROIC | Return on Invested Capital |
| | ROE | Return on Equity |
| | Operating Margin | Operating Income / Revenue |
| | Net Margin | Net Income / Revenue |
| **Cash Generation** | Free Cash Flow | Operating CF - CapEx |
| | Owner Earnings | Net Income + D&A - CapEx |
| | CapEx Ratio | CapEx / Operating CF |
| **Financial Strength** | Debt-to-Equity | Total Liabilities / Equity |
| | Interest Coverage | EBIT / Interest Expense |
| **Capital Allocation** | Dividend Yield | Annual Dividend / Price |
| | Payout Ratio | Dividends / Net Income |

All metric calculations handle missing data gracefully and provide warnings when calculations can't be completed.

---

## 5. Complete Workflow Example

Here's a typical end-to-end workflow:

```bash
# 1. Add API keys
python3 -m cli.api_keys_cli add polygon.io YOUR_POLYGON_KEY
python3 -m cli.api_keys_cli add alpha_vantage YOUR_AV_KEY

# 2. Create a watchlist
python3 -m cli.watchlist_cli add AAPL --company "Apple Inc"
python3 -m cli.watchlist_cli add MSFT --company "Microsoft Corp"
python3 -m cli.watchlist_cli list

# 3. Fetch raw data
python3 -m cli.data_fetch_cli run

# 4. Calculate metrics
python3 -m cli.metrics_cli calculate-watchlist

# 5. View results
python3 -m cli.metrics_cli show AAPL
python3 -m cli.metrics_cli show MSFT
```

---

## 6. Data Storage Structure

The toolkit maintains strict separation between raw API data and computed metrics:

```
data/
├── raw/                          # Raw API data (never contains calculated values)
│   ├── AAPL/
│   │   ├── latest.json          # Most recent raw data
│   │   └── history/             # Historical snapshots
│   │       └── 2025-10-14T00-19-58.json
│   └── MSFT/
│       ├── latest.json
│       └── history/
├── metrics/                      # Calculated metrics (computed from raw data)
│   ├── AAPL/
│   │   ├── latest.json          # Most recent metrics
│   │   └── history/             # Historical calculations
│   │       └── 2025-10-14T00-57-34.json
│   └── MSFT/
│       ├── latest.json
│       └── history/
└── watchlists/                   # Watchlist definitions
    ├── default.json
    └── income_funds.json
```

### Programmatic Access

```python
from storage.json_store import JsonStore

store = JsonStore()

# List all tickers with data
tickers = store.list_tickers()
print(tickers)  # ['AAPL', 'MSFT']

# Read raw data
raw_snapshot = store.read_raw_snapshot("AAPL")
print(raw_snapshot.financials)

# Read metrics
metrics_snapshot = store.read_metrics_snapshot("AAPL")
print(metrics_snapshot.valuation)

# List history
raw_history = store.list_raw_history("AAPL")
metrics_history = store.list_metrics_history("AAPL")
```

---

## 7. Configuration & Customization

### 7.1 Data Source Mapping

Fine-tune `config/data_source_mapping.yaml` to:
- Add new data fields
- Override provider priorities
- Configure fallback providers

Example:
```yaml
financials.revenue:
  primary: polygon.io
  secondary: alpha_vantage
  tertiary: yahoo_finance
  endpoint: /vX/reference/financials
```

### 7.2 Metric Catalog

Refer to `config/metric_catalog.yaml` for:
- Metric definitions and formulas
- Required data points
- Technical implementation details

Each metric includes:
- **Display Name**: Human-readable name
- **End User Definition**: Plain English explanation
- **Technical Definition**: Mathematical formula
- **Data Points**: Required fields from raw data

---

## 8. Tips & Troubleshooting

### Missing Data
- The system uses fallback providers automatically
- Check warnings in CLI output for missing fields
- Yahoo Finance may rate-limit; wait a few minutes between runs

### API Keys
- Primary provider (Polygon.io) is **required**
- Secondary providers improve data completeness
- Keys can be set via environment variables or stored credentials

### Data Quality
- Always review warnings after data fetch
- Historical snapshots allow data quality tracking over time
- Metrics with missing inputs will be skipped with warnings

---

## 9. Advanced Usage

For deeper implementation details, architecture documentation, and development guidance:

- **Technical Specification**: `technical_spec.md`
- **Implementation Overview**: `IMPLEMENTATION_OVERVIEW.md`
- **Data Source Configuration**: `config/DATA_SOURCE_README.md`
- **Metric Definitions**: `config/metric_catalog.yaml`

Happy investing! 📈
