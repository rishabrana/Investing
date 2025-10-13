# Investing Toolkit Overview

This project provides a small Python toolkit that helps value-oriented investors retrieve high-quality fundamentals, persist them locally, and build automation around Buffett-style metrics. The major components are:

- **JsonStore** (in `storage/json_store.py`): Local JSON-based datastore for raw API data, computed metrics, and watchlist definitions.
- **DataIngestionService** (in `services/data_ingestion_service.py`): Orchestrates multi-provider data fetching, normalization, and persistence.
- **Watchlist CLI** (in `cli/watchlist_cli.py`): Simple command-line tool for managing ticker watchlists.

The sections below describe how to get started, manage watchlists, and refresh data.

---

## 1. Quick Start

1. **Create / activate the virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Create the initial data directory structure**
   - The `JsonStore` automatically creates folders (e.g., `./data/raw`, `./data/watchlists`) the first time you run the CLI or ingestion service.
3. **Provide API keys**
   - Either set environment variables (`POLYGON_API_KEY`, `FMP_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `FINNHUB_API_KEY`), *or*
   - Use the bundled credentials CLI (see §2.1) to store keys securely in `./data/credentials/api_keys.json`.
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

`DataIngestionService` orchestrates the entire acquisition workflow:

1. Derives the fields required for each ticker.
2. Uses `DataSourceRouter` to minimize API calls across providers (Polygon.io, Financial Modeling Prep, Alpha Vantage, Finnhub, Yahoo).
3. Normalizes payloads.
4. Writes raw snapshots to `JsonStore`.

### 3.1 CLI Runner

Run the data fetch pipeline from the command line:

```bash
python -m cli.data_fetch_cli run
```

Optional flags:

- `--watchlist income_funds` – use a non-default watchlist
- `--period quarterly` – pull quarterly statements instead of annual
- `--resume` – skip tickers already processed in the previous run
- `--max-tickers 5` – limit the number of tickers in this run
- `--no-history` – only write the latest snapshot

Before fetching, the CLI verifies credentials:

- **Primary provider (Polygon.io)**: if no key is found (environment variable `POLYGON_API_KEY` or stored credential), the command prints an error and exits.
- **Secondary providers** (`financial_modeling_prep`, `alpha_vantage`, `finnhub.io`): missing keys trigger warnings so you know fallback data might be unavailable.

To create a seeded watchlist directly in the store:

```bash
python -m cli.data_fetch_cli create-sample-watchlist --watchlist demo
```

### 3.2 Minimal programmatic example

```python
from storage.json_store import JsonStore, load_watchlist_from_store
from services import DataIngestionService, DataSourceRouter, Normalizer

store = JsonStore()
watchlist = load_watchlist_from_store(store)

router = DataSourceRouter()
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

### CLI wrappers (planned)

At present, the ingestion service is primarily used programmatically. You can wrap it in scripts or future CLI commands to schedule daily refreshes, etc.

---

## 4. Inspecting Stored Data

- Raw snapshots: `./data/raw/<TICKER>/latest.json` (history in `./data/raw/<TICKER>/history/`).
- Metrics snapshots (once implemented): `./data/metrics/<TICKER>/`.
- Watchlists: `./data/watchlists/<NAME>.json`.

Use the helper functions in `storage/json_store.py`:

```python
from storage.json_store import JsonStore

store = JsonStore()
tickers = store.list_tickers()
print(tickers)

snapshot = store.read_raw_snapshot("AAPL")
print(snapshot)
```

---

## 5. Tips & Next Steps

- **Configuration-driven sourcing**: Fine-tune `config/data_source_mapping.yaml` to add new fields or override providers.
- **Metrics**: Refer to `config/metric_catalog.yaml` for metric definitions and to `technical_spec.md` for the full architecture.
- **Future CLI expansion**: Potential commands for triggering `DataIngestionService`, computing metrics, or exporting reports.

For deeper implementation detail, check `technical_spec.md` and `IMPLEMENTATION_OVERVIEW.md`.

Happy investing!
