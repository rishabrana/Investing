# Technical Specification — Value Investor Metrics Collector

## 1. Overview
- **Purpose**: Provide a Python-based toolchain that pulls Buffett-style fundamental metrics from prioritized market data providers (Polygon.io, Financial Modeling Prep, Alpha Vantage, Finnhub, Yahoo Finance fallback), stores normalized snapshots in a local JSON datastore, and exposes reusable functions for downstream consumers (future web API, CLI utilities).
- **Primary Users**: Retail investors and analysts who want quick access to intrinsic-value-centric metrics (as defined in `Ideas for value investor.md`).
- **Deliverables**: Python package, local JSON database directory, two text-based CLI entry points (`data_fetch` and `metrics_cli`).

## 2. Scope
- **In Scope**
  - Reading a YAML watchlist (tickers + optional metadata).
  - Fetching raw fundamentals and market data from prioritized API providers (Polygon.io, Financial Modeling Prep, Alpha Vantage, Finnhub, Yahoo Finance fallback).
  - Calculating a curated subset of value-investing metrics.
  - Persisting snapshots to disk in JSON.
  - Text-based CLI for batch data refresh and metric inspection.
  - Public service layer functions ready for future web/REST wrapper.
- **Out of Scope**
  - Building a web server or REST API.
  - Advanced screening workflows or UI.
  - Portfolio analytics beyond specified metrics.
  - Writing to external databases other than local JSON.

## 3. High-Level Architecture
```
watchlist.yaml ─▶ CLI:data_fetch ─▶ DataIngestionService ─▶ JsonStore
                                      │          ▲              │
                                      ▼          │              ▼
                           DataSourceRouter      │       MetricsService
                         (driven by mapping)     │              ▲
                                      │          │              │
                  data_source_mapping.yaml ──────┘       CLI:metrics_cli
                                      │
                                      ▼
                          API Clients (Polygon.io, FMP, Alpha Vantage, Finnhub, Yahoo)
metrics_config.yaml ───────────────────────────────────────────────────────┘
```

- **Configuration Layer**: Loads environment variables (API keys, data directory paths, rate limits, metric profiles, data source mapping).
- **DataIngestionService**: Coordinates watchlist parsing, delegates field acquisition to the router, normalizes payloads, and persists without depending on metric logic.
- **DataSourceRouter**: Plans provider/endpoint batches using `data_source_mapping.yaml`, invokes provider-specific clients, and aggregates results with source attribution.
- **API Clients**: Provider-specific adapters (Polygon.io, Financial Modeling Prep, Alpha Vantage, Finnhub, Yahoo Finance) that share retry/rate-limit utilities.
- **RateLimiter**: Shared utility that enforces configurable request pacing per provider (defaults align with free tiers).
- **Normalizer**: Transforms raw API responses into consistent schema used by the datastore.
- **JsonStore**: Handles read/write operations to a local JSON database.
- **MetricsService**: Computes key metrics from stored snapshots based on configurable metric sets and exposes structured results.
- **CLI Entry Points**:
  - `data_fetch`: Reads watchlist, refreshes data for each ticker via `DataIngestionService`, writes to JSON store.
  - `metrics_cli`: Accepts ticker(s), reads from store, applies selected metric set via `MetricsService`, and prints/scaffolds outputs.

## 4. External Interfaces
- **Polygon.io API**
  - `GET /v3/reference/tickers/{ticker}` for company metadata.
  - `GET /vX/reference/financials` (Quarterly & annual fundamentals).
  - `GET /v2/aggs/ticker/{ticker}/prev` for latest close price.
  - `GET /v2/reference/news` (optional for future expansion).
- **Environment Variables**
  - `POLYGON_API_KEY` (required).
  - `FMP_API_KEY` (optional but required for Financial Modeling Prep data).
  - `ALPHA_VANTAGE_API_KEY` (optional but required for Alpha Vantage data).
  - `FINNHUB_API_KEY` (optional but required for Finnhub data).
  - `DATA_DIR` (optional, default `./data`).
  - `POLYGON_REQUESTS_PER_MINUTE` (optional, default `4` to stay within free-tier allowance with buffer).
  - `POLYGON_REQUEST_SLEEP_SECONDS` (optional per-call minimum delay override).
  - `METRICS_CONFIG_PATH` (optional, default `./config/metrics_config.yaml`).
  - `METRIC_CATALOG_PATH` (optional, default `./config/metric_catalog.yaml`).
  - `DATA_SOURCE_MAPPING_PATH` (optional, default `./config/data_source_mapping.yaml`).
- **Input YAML (watchlist)**
  ```yaml
  default_metrics_profile: buffett_core
  tickers:
    - symbol: AAPL
      name: Apple Inc
      notes: Consumer tech moat
      metrics_profile: wide_moat_focus
  ```
- **Metrics Configuration YAML**
  ```yaml
  profiles:
    buffett_core:
      metrics:
        - margin_of_safety
        - free_cash_flow
        - return_on_invested_capital
        - debt_to_equity_and_interest_coverage
        - operating_and_net_margin
        - economic_moat_score
    wide_moat_focus:
      extends: buffett_core
      metrics:
        - book_value_per_share_growth
        - return_on_equity
        - consistency_score
  ```
- **Data Source Mapping YAML**
  ```yaml
  data_sources:
    price.close:
      primary: polygon.io
      endpoint: /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}
      field: close
    financials.retained_earnings:
      primary: alpha_vantage
      secondary: yahoo_finance
      endpoint: BALANCE_SHEET
      field: retainedEarnings
    assumptions.beta:
      primary: financial_modeling_prep
      secondary: yahoo_finance
      endpoint_fmp: /profile/{ticker}
      field_fmp: beta
  api_priority:
    - polygon.io
    - financial_modeling_prep
    - alpha_vantage
    - finnhub
    - yahoo_finance
  ```

## 5. Data Acquisition Strategy
- **DataSourceRouter**: At runtime, loads `data_source_mapping.yaml` and `api_priority` order to build a sourcing plan for every required field.
- **Mapping Semantics**: Each mapping entry specifies field identifiers, provider endpoints, extraction hints (field names, statements), and optional fallbacks; router keeps the schema authoritative so code stays configuration-driven.
- **Batch Planning**: Groups requested data points per provider/endpoint/timeframe so the fewest per-ticker HTTP calls retrieve the widest set of fields (e.g., pulls all Polygon financial statement fields using a single `/vX/reference/financials` request when the mapping indicates they share the endpoint).
- **Field Extraction**: After each response, adapter plugins normalize payloads (Polygon, Financial Modeling Prep, Alpha Vantage, Finnhub, Yahoo Finance) and emit the standardized field/value pairs back to the router.
- **Fallback Handling**: If a primary provider fails or omits a field, the router automatically advances to the secondary/tertiary providers defined in the mapping without duplicating already-collected data.
- **Priority Rules**: `api_priority` order in the YAML drives which provider is attempted first; ticker-specific overrides can be introduced by extending the mapping schema.
- **Caching & Reuse**: Responses are cached within a run so multiple metrics needing the same payload reuse it rather than triggering redundant API calls.
- **Rate Limit Awareness**: Router cooperates with `RateLimiter` to respect per-provider caps, backing off and queueing calls based on provider-specific throttle settings from the mapping file.
- **Extensibility**: New data providers require only YAML updates plus a lightweight adapter implementing extraction logic; no core ingestion code changes.

## 6. Data Storage Design
- **Location**: `${DATA_DIR}/snapshots/{ticker}.json`
- **Schema (per ticker)**
  ```json
  {
    "ticker": "AAPL",
    "as_of": "2024-03-31",
    "price": {
      "close": 175.12,
      "source": "polygon_prev_close"
    },
    "financials": {
      "period": "annual",
      "fiscal_year": 2023,
      "revenue": 383285000000,
      "net_income": 96995000000,
      "operating_income": 114301000000,
      "income_tax_expense": 16467000000,
      "pre_tax_income": 113532000000,
      "operating_cash_flow": 110543000000,
      "capital_expenditure": 10959000000,
      "total_assets": 352755000000,
      "total_liabilities": 290437000000,
      "total_debt": 98787000000,
      "cash_and_equivalents": 29965000000,
      "shareholders_equity": 62497000000,
      "shares_outstanding": 15613000000,
      "interest_expense": 3904000000,
      "ebit": 114300000000,
      "depreciation_amortization": 11104000000,
      "other_non_cash_charges": 2450000000
    },
    "market_data": {
      "market_cap": 2740000000000
    },
    "cash_flow": {
      "dividends_paid": 15000000000,
      "annual_dividend_per_share": 0.96
    },
    "assumptions": {
      "wacc": 0.07
    },
    "derived": {
      "fcf": 99584000000,
      "owner_earnings": 100648000000
    },
    "source_metadata": {
      "price.close": {"provider": "polygon.io", "timestamp": "2024-04-01T20:00:00Z"},
      "financials.retained_earnings": {"provider": "alpha_vantage", "fetched_at": "2024-04-05T12:05:00Z"}
    },
    "raw": {
      "financials_payload": { "...": "original API payload snapshot" }
    }
  }
  ```
- **Retention**: Maintain most recent snapshot by default; optionally keep history under `${DATA_DIR}/history/{ticker}/{timestamp}.json` (configurable flag).
- **Source Attribution**: `source_metadata` tracks which provider satisfied each field, enabling auditing, caching, and targeted refresh when data-source priorities change.

## 7. Metrics Configuration & Catalog
- Metric calculations are profile-driven: each CLI call or downstream consumer can specify a metric profile loaded from `metrics_config.yaml`. Profiles define metric identifiers and optional overrides (e.g., horizon, scoring weights).
- `MetricsService` is decoupled from data ingestion; it reads normalized snapshots and applies only the metrics requested.

### 7.1 Metric Profiles
- `MetricsService.load_profile(profile_name)` merges profile definitions (supports `extends` inheritance) and resolves metric list/order.
- Tickers may override the default profile via watchlist entry (`metrics_profile`), or callers can supply `metrics` list explicitly to `get_metrics`.
- Unsupported metrics result in a validation error before calculations run.

### 7.2 Metric Catalog Source
- Canonical definitions for all 20 Buffett-style metrics reside in `config/metric_catalog.yaml`.
- Each entry captures:
  - `display_name` for UI/CLI presentation.
  - `end_user_definition` written for investors.
  - `technical_definition` with explicit formulas and calculation logic.
  - `data_points`, listing the normalized fields and assumption inputs required.
- `config/metrics_loader.py` parses the YAML, validates requested identifiers, and surfaces the metadata to `MetricsService`.
- Analysts can extend or edit definitions by modifying the YAML without changing Python modules. Validation fails fast if required fields are missing.

### 7.3 Metrics Overview
- Current catalog (in `config/metric_catalog.yaml`) includes, in order: `margin_of_safety`, `free_cash_flow`, `return_on_invested_capital`, `return_on_equity`, `debt_to_equity_and_interest_coverage`, `eps_growth`, `book_value_per_share_growth`, `price_to_earnings`, `price_to_book`, `ev_to_ebitda`, `peg_ratio`, `operating_and_net_margin`, `owner_earnings`, `return_on_retained_earnings`, `economic_moat_score`, `consistency_score`, `capital_expenditure_ratio`, `dividend_yield_and_payout_ratio`, `wacc_vs_roic_spread`, `ten_year_average_roce`.
- Additional metrics can be appended by adding new YAML blocks that provide the same four metadata fields and by updating profiles to reference the new slug.

### 7.4 Output Format
- `MetricsService.get_metrics(ticker, profile="buffett_core")` returns a payload that includes metadata about which metrics were applied.
  ```python
  {
      "ticker": "AAPL",
      "as_of": "2024-03-31",
      "metrics_included": [
          "margin_of_safety",
          "free_cash_flow",
          "return_on_invested_capital",
          "economic_moat_score"
      ],
      "valuation": {"margin_of_safety": 0.18, "price_to_earnings": 22.5, "price_to_book": 6.8, "ev_to_ebitda": 15.2},
      "profitability": {"return_on_invested_capital": 0.14, "return_on_equity": 0.28, "operating_margin": 0.32, "net_margin": 0.25},
      "cash_generation": {"free_cash_flow": 99584000000, "fcf_yoy_growth": 0.05, "owner_earnings": 100648000000},
      "financial_strength": {"debt_to_equity": 0.46, "interest_coverage": 29.3},
      "capital_allocation": {"return_on_retained_earnings": 0.18},
      "moat": {"economic_moat_score": "wide", "supporting_indicators": {...}},
      "notes": ["Stable margins over 10 yrs", "High ROIC vs WACC (7%)"]
  }
  ```

## 8. Module Breakdown
- `config.py`
  - Loads environment variables, default paths, rate-limit configs (calls/minute, sleep between calls), and metrics configuration path.
- `config/metrics_loader.py`
  - Parses `metrics_config.yaml` and `metric_catalog.yaml`, resolves profile inheritance, and validates metric identifiers and required data bindings.
- `config/data_source_loader.py`
  - Parses `data_source_mapping.yaml`, normalizes provider priority, endpoint templates, and field mappings; exposes helper methods for lookup and validation.
- `clients/polygon_client.py`
  - Dependency: `requests` (or `httpx`).
  - Methods: `get_company_profile`, `get_financials(ticker, limit, timeframe)`, `get_previous_close`.
  - Handles retries, HTTP errors, API key injection, rate limiting, and paced request queue (token bucket).
- `clients/fmp_client.py`, `clients/alpha_vantage_client.py`, `clients/finnhub_client.py`, `clients/yahoo_client.py`
  - Provide thin wrappers around each external API with shared base functionality (auth, rate limit coordination, response normalization hooks).
- `services/data_source_router.py`
  - Builds optimal call batches per provider using mapping metadata, minimizes HTTP round-trips by coalescing fields that share endpoints, executes calls through provider clients, and yields normalized field/value sets with source attribution.
- `services/data_ingestion.py`
  - Stateless orchestrator that consumes watchlist definitions, derives required field sets from metrics/config, asks `data_source_router` for those fields, coordinates rate limiting, normalizes responses, and persists via `JsonStore`.
  - Exposes `refresh_ticker` and `refresh_watchlist` without depending on metric code.
- `storage/json_store.py`
  - Methods: `read_snapshot(ticker)`, `write_snapshot(ticker, payload)`, `list_snapshots()`.
  - Ensures atomic writes (temp file + rename).
- `services/normalizer.py`
  - Converts raw provider payloads to normalized schema.
  - Calculates derived fields directly available (e.g., FCF).
- `services/metrics_service.py`
  - Consumes normalized data, calculates metrics defined in §7 using requested profile or explicit metric list.
  - Exposes `get_metrics(ticker, profile=None, metrics=None)` and `get_bulk_metrics(tickers, profile=None, metrics=None)`.
- `cli/data_fetch.py`
  - Args: `--input watchlist.yaml`, `--period annual|quarterly`, `--history`.
  - Optional rate parameters: `--max-per-minute`, `--sleep-override`, `--resume` (skip tickers already updated this run).
  - Flow: load tickers → invoke `DataIngestionService.refresh_watchlist` → normalize → store snapshots.
  - Provides progress logging, persistence of fetch progress, and summary with throttling stats.
- `cli/metrics_cli.py`
  - Args: `--ticker AAPL` or `--input watchlist.yaml`.
  - Metric selection flags: `--profile buffett_core`, `--metric margin_of_safety --metric return_on_invested_capital`.
  - Outputs formatted text table or JSON.
  - Optionally dumps raw data for debugging.
- `utils/calculations.py`
  - Shared formula functions (ROIC, ROE, growth rates, CAGR).
- `utils/logger.py`
  - Configures `logging` with CLI-friendly formatting.

## 9. Resilience, Error Handling & Logging
- Use structured logging (JSON optional) with log levels.
- Categorize failures: configuration errors, API errors (429, network), data quality (missing fields).
- Client applies token-bucket rate limiting with provider-specific pacing (e.g., Polygon 4 req/min buffer) plus jittered sleep to remain below free-tier caps.
- Retries with exponential backoff for HTTP 429/5xx, escalating to slow mode (longer sleep) after consecutive failures.
- `data_fetch` writes per-run progress file (`${DATA_DIR}/logs/fetch_state.json`) to allow resume after interruption.
- Partial failures recorded in run report with clear status per ticker.
- DataSourceRouter records provider fallbacks and partial payload coverage, enabling targeted retries or manual overrides.

## 10. Testing Strategy
- **Unit Tests**
  - Polygon client: request construction, retry logic (use responses/pytest-mock).
  - Data source router: grouping logic, fallback sequencing, caching reuse.
  - Normalizer: sample payload fixtures → expected normalized schema.
  - Metrics calculations: deterministic inputs → expected metrics.
- **Integration Tests**
  - Mocked multi-provider endpoints (via VCR.py) to verify end-to-end CLI run across fallback scenarios.
  - CLI command tests using `pytest` + `click.testing.CliRunner` (if Click used) or `subprocess`.
- **Data Validation**
  - Schema validation (pydantic or custom) before writing snapshots.
  - Guardrails for divide-by-zero, insufficient history (return `None` with warning).

## 11. Deployment & Execution
- **Dependencies**: `requests`, `python-dateutil`, `pydantic` (or lightweight schema), `click` (optional for CLI UX).
- **Runtime**: Python 3.11+.
- **Install**: `pip install -r requirements.txt`.
- **Usage**
  1. Export `POLYGON_API_KEY` and review/edit `config/metrics_config.yaml`, `config/metric_catalog.yaml`, and `config/data_source_mapping.yaml` as needed.
  2. `python -m cli.data_fetch --input watchlist.yaml --period annual --max-per-minute 4`.
  3. `python -m cli.metrics_cli --ticker AAPL --format table --profile buffett_core`.
- **Packaging**: Standard Python package with `pyproject.toml`.

## 12. Security & Privacy
- Store API key outside source control (env var or `.env` ignored).
- JSON datastore resides locally; no PII expected.
- Optionally encrypt data directory for multi-user environments (future enhancement).

## 13. Future Enhancements
- Replace JSON store with SQLite for richer querying.
- Add asynchronous fetch pipeline for large watchlists.
- Build FastAPI wrapper around `MetricsService`.
- Introduce caching and rate limit coordination across runs.
- Integrate scenario-based intrinsic value models.

## Appendix A — Metric Inputs
- **Intrinsic Value**: Requires projected cash flows, discount rate (config), terminal growth assumptions (config defaults).
- **ROIC**: Uses NOPAT (from financials) ÷ Invested Capital (equity + debt - non-operating assets).
- **Return on Retained Earnings**: `(Change in Market Cap - Dividends Paid) ÷ Retained Earnings`.
- **Moat Score**: Weighted rules on ROIC trend, margin stability (std dev thresholds), revenue CAGR, debt levels.
- **WACC**: Configurable defaults (e.g., 7%) with ability to override per ticker via watchlist metadata.
