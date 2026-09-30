# CLAUDE.md

Instructions for Claude Code when working in this repository.

## Project

Investment Analysis Toolkit — a Buffett/Munger-style stock analysis app: a
Python/FastAPI backend that fetches fundamentals from multiple data
providers, computes investment metrics, and a React/TypeScript frontend for
browsing stocks, running screens, and managing a watchlist. Runs entirely
locally; API keys stay on the user's machine. See `README.md` for setup and
`DETAILED_DOCS.md` / `IMPLEMENTATION_OVERVIEW.md` for deeper design notes.

## Structure

- `backend/api/` — FastAPI app (`main.py`), routes (`stocks`, `screener`,
  `watchlist`, `settings`, `logs`, `health`)
- `clients/` — data provider clients: Polygon.io (primary), Alpha Vantage,
  Financial Datasets, SEC EDGAR, Yahoo Finance
- `services/` — data ingestion/routing (`data_source_router.py`,
  `data_ingestion_service.py`), metric calculation
  (`metric_calculator.py`, `metrics_service.py`), field normalization
- `storage/` — local JSON-backed persistence (`json_store.py`)
- `cli/` — `api_keys_cli.py`, `data_fetch_cli.py`, `metrics_cli.py`,
  `watchlist_cli.py`
- `config/` — `metric_catalog.yaml`, `data_source_mapping.yaml`
- `frontend/` — React + TypeScript app (Vite); `src/components/` grouped by
  feature (stock, screener, watchlist, settings, metrics, logs)
- `tests/` — pytest suite for metric calculation/accuracy

## Conventions

- Backend: `PYTHONPATH=$(pwd) python3 -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000`.
  Frontend: `cd frontend && npm run dev`. Or use `./runme.sh` for both.
- Install via `./installme.sh`; configure via `python -m cli.api_keys_cli add <provider> <key>`.
- **API keys are user data, not config** — stored via the CLI/Settings UI into
  `data/logs/credentials/api_keys.json`, which is gitignored (`logs/` and
  `*api_keys*.json` patterns). Never hardcode a provider key in source.
- `data/raw/`, `data/metrics/`, `data/watchlists/` are gitignored — per-user
  data, not shared across machines.
- `frontend/node_modules/` is gitignored — install with `npm install`, don't
  commit it. (It was previously tracked by mistake; that history was cleaned
  up in a repo-hygiene pass — always double check `git status` after
  `npm install` doesn't re-add it.)
- `__pycache__/` / `*.pyc` are gitignored — if `git status` ever shows one as
  tracked, `git rm --cached` it.
