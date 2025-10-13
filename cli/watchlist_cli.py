"""
Command-line utilities for managing watchlists stored in JsonStore.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from storage.json_store import JsonStore, Watchlist, WatchlistEntry


def get_store(data_dir: Optional[str]) -> JsonStore:
    """Create a JsonStore using the provided data directory."""
    if data_dir:
        return JsonStore(data_dir=data_dir)
    return JsonStore()


def load_or_create_watchlist(store: JsonStore, name: str) -> Watchlist:
    """Load an existing watchlist or create a new empty one."""
    watchlist = store.load_watchlist(name)
    if watchlist is None:
        watchlist = Watchlist(tickers=[])
    return watchlist


def cmd_list(args: argparse.Namespace) -> int:
    """List all tickers in the watchlist."""
    store = get_store(args.data_dir)
    watchlist = store.load_watchlist(args.name)

    if watchlist is None or not watchlist.tickers:
        print(f"No entries found in watchlist '{args.name}'.")
        return 0

    print(f"Watchlist '{args.name}' (default profile: {watchlist.default_metrics_profile})")
    print("-" * 72)
    print(f"{'Symbol':<12} {'Name':<30} {'Metrics Profile':<20}")
    print("-" * 72)
    for entry in watchlist.tickers:
        profile = entry.metrics_profile or watchlist.default_metrics_profile
        print(f"{entry.symbol:<12} {entry.name:<30} {profile:<20}")
    print("-" * 72)
    print(f"Total: {len(watchlist.tickers)} ticker(s)")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add a ticker to the watchlist."""
    store = get_store(args.data_dir)
    watchlist = load_or_create_watchlist(store, args.name)

    symbol = args.symbol.upper()
    if any(entry.symbol == symbol for entry in watchlist.tickers):
        print(f"{symbol} is already in watchlist '{args.name}'.")
        return 1

    entry = WatchlistEntry(
        symbol=symbol,
        name=args.company or symbol,
        notes=args.notes,
        metrics_profile=args.profile,
        custom_fields={}
    )

    watchlist.tickers.append(entry)
    if args.default_profile:
        watchlist.default_metrics_profile = args.default_profile

    store.save_watchlist(watchlist, name=args.name)
    print(f"Added {symbol} to watchlist '{args.name}'.")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a ticker from the watchlist."""
    store = get_store(args.data_dir)
    watchlist = store.load_watchlist(args.name)

    if watchlist is None:
        print(f"Watchlist '{args.name}' not found.")
        return 1

    symbol = args.symbol.upper()
    filtered = [entry for entry in watchlist.tickers if entry.symbol != symbol]

    if len(filtered) == len(watchlist.tickers):
        print(f"{symbol} not found in watchlist '{args.name}'.")
        return 1

    watchlist.tickers = filtered
    store.save_watchlist(watchlist, name=args.name)
    print(f"Removed {symbol} from watchlist '{args.name}'.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Manage watchlists stored in JsonStore.")
    parser.add_argument(
        "--data-dir",
        help="Base directory for JsonStore (default: ./data)",
    )
    parser.add_argument(
        "--name",
        default="default",
        help="Watchlist name to operate on (default: default)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List tickers in the watchlist")
    list_parser.set_defaults(func=cmd_list)

    add_parser = subparsers.add_parser("add", help="Add a ticker to the watchlist")
    add_parser.add_argument("symbol", help="Ticker symbol (e.g., AAPL)")
    add_parser.add_argument("--company", help="Company name")
    add_parser.add_argument("--notes", help="Optional notes")
    add_parser.add_argument("--profile", help="Metrics profile override for this ticker")
    add_parser.add_argument(
        "--default-profile",
        help="Optional default profile for the watchlist (updates on save)",
    )
    add_parser.set_defaults(func=cmd_add)

    remove_parser = subparsers.add_parser("remove", help="Remove a ticker from the watchlist")
    remove_parser.add_argument("symbol", help="Ticker symbol to remove")
    remove_parser.set_defaults(func=cmd_remove)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the watchlist CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
