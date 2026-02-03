"""
Command-line entry point for running the DataIngestionService.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Tuple, List

from clients import PolygonClient, AlphaVantageClient, YahooFinanceClient, FinancialDatasetsClient
from services import DataIngestionService, DataSourceRouter, Normalizer
from storage.json_store import (
    API_ENV_MAP,
    JsonStore,
    create_sample_watchlist,
    load_watchlist_from_store,
)

# Provider priority definitions (align with technical spec)
PRIMARY_PROVIDERS: List[str] = ["polygon.io"]
SECONDARY_PROVIDERS: List[str] = [
    "financial_datasets",
    "financial_modeling_prep",
    "alpha_vantage",
    "finnhub.io",
]


def get_store(data_dir: Optional[str]) -> JsonStore:
    """Instantiate JsonStore with an optional custom data directory."""
    if data_dir:
        return JsonStore(data_dir=data_dir)
    return JsonStore()


def validate_api_keys(store: JsonStore) -> Tuple[List[str], List[str]]:
    """
    Ensure that required API keys are available.

    Returns:
        Tuple of (missing_primary, missing_secondary)
    """
    missing_primary = []
    missing_secondary = []

    for provider in PRIMARY_PROVIDERS:
        if not store.get_api_key(provider):
            missing_primary.append(provider)

    for provider in SECONDARY_PROVIDERS:
        if not store.get_api_key(provider):
            missing_secondary.append(provider)

    return missing_primary, missing_secondary


def provider_hint(provider: str) -> str:
    """Return a helpful hint for resolving a missing API key."""
    env_var = API_ENV_MAP.get(provider)
    if env_var:
        return (
            f"Set environment variable {env_var} or run "
            f"'python -m cli.api_keys_cli add {provider} <API_KEY>'."
        )
    return "No API key required for this provider."


def cmd_run(args: argparse.Namespace) -> int:
    """Execute the data fetch workflow."""
    store = get_store(args.data_dir)

    try:
        watchlist = load_watchlist_from_store(store, name=args.watchlist)
    except FileNotFoundError:
        print(
            f"ERROR: Watchlist '{args.watchlist}' not found. "
            "Create one with the watchlist CLI or JsonStore helpers.",
            file=sys.stderr,
        )
        return 1

    missing_primary, missing_secondary = validate_api_keys(store)

    if missing_primary:
        for provider in missing_primary:
            print(
                f"ERROR: Missing API key for primary provider '{provider}'. "
                f"{provider_hint(provider)}",
                file=sys.stderr,
            )
        return 1

    if missing_secondary:
        for provider in missing_secondary:
            print(
                f"Warning: Missing API key for secondary provider '{provider}'. "
                f"{provider_hint(provider)}",
                file=sys.stderr,
            )

    clients = {}

    # Initialize Financial Datasets client (preferred primary)
    fd_key = store.get_api_key("financial_datasets")
    if fd_key:
        try:
            clients["financial_datasets"] = FinancialDatasetsClient(fd_key)
        except ValueError as exc:
            print(f"Warning: {exc}", file=sys.stderr)

    # Initialize Polygon client
    polygon_key = store.get_api_key("polygon.io")
    if polygon_key:
        try:
            clients["polygon.io"] = PolygonClient(polygon_key)
        except ValueError as exc:  # pragma: no cover
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    # Initialize Alpha Vantage client
    alpha_vantage_key = store.get_api_key("alpha_vantage")
    if alpha_vantage_key:
        try:
            clients["alpha_vantage"] = AlphaVantageClient(alpha_vantage_key)
        except ValueError as exc:  # pragma: no cover
            print(f"Warning: {exc}", file=sys.stderr)

    # Initialize Yahoo Finance client (no API key required)
    try:
        clients["yahoo_finance"] = YahooFinanceClient()
    except ImportError as exc:
        print(f"Warning: Yahoo Finance client unavailable: {exc}", file=sys.stderr)

    router = DataSourceRouter(clients=clients)
    normalizer = Normalizer()
    service = DataIngestionService(
        json_store=store,
        data_source_router=router,
        normalizer=normalizer,
        period=args.period,
        save_history=not args.no_history,
    )

    summary = service.refresh_watchlist(
        watchlist=watchlist,
        resume=args.resume,
        max_tickers=args.max_tickers,
    )

    print("Data fetch complete. Summary:")
    print(json.dumps(summary, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for data fetching."""
    parser = argparse.ArgumentParser(description="Run data ingestion for a watchlist.")
    parser.add_argument(
        "--data-dir",
        help="Base directory for JsonStore (default: ./data)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Fetch data for a watchlist")
    run_parser.add_argument(
        "--watchlist",
        default="default",
        help="Watchlist name to process (default: default)",
    )
    run_parser.add_argument(
        "--period",
        choices=["annual", "quarterly"],
        default="annual",
        help="Financial period to request (default: annual)",
    )
    run_parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous fetch state if available.",
    )
    run_parser.add_argument(
        "--max-tickers",
        type=int,
        help="Limit the number of tickers processed in this run.",
    )
    run_parser.add_argument(
        "--no-history",
        action="store_true",
        help="Skip writing historical snapshots (latest only).",
    )
    run_parser.set_defaults(func=cmd_run)

    seed_parser = subparsers.add_parser(
        "create-sample-watchlist",
        help="Create a sample watchlist in the store.",
    )
    seed_parser.add_argument(
        "--watchlist",
        default="sample",
        help="Name for the sample watchlist (default: sample)",
    )
    seed_parser.set_defaults(func=cmd_create_sample_watchlist)

    return parser


def cmd_create_sample_watchlist(args: argparse.Namespace) -> int:
    """Create a sample watchlist via JsonStore helpers."""
    store = get_store(args.data_dir)
    create_sample_watchlist(store=store, name=args.watchlist)
    print(f"Sample watchlist '{args.watchlist}' created.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
