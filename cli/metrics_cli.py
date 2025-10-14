"""
Command-line entry point for calculating investment metrics.

This CLI provides commands for:
- Calculating metrics for individual tickers
- Calculating metrics for entire watchlists
- Viewing calculated metrics
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from services import MetricsService
from storage.json_store import JsonStore


def get_store(data_dir: Optional[str]) -> JsonStore:
    """Instantiate JsonStore with an optional custom data directory."""
    if data_dir:
        return JsonStore(data_dir=data_dir)
    return JsonStore()


def cmd_calculate_ticker(args: argparse.Namespace) -> int:
    """Calculate metrics for a single ticker."""
    store = get_store(args.data_dir)
    service = MetricsService(json_store=store)

    try:
        snapshot = service.calculate_metrics(
            ticker=args.ticker,
            profile=args.profile,
            save_history=not args.no_history
        )

        print(f"✓ Calculated metrics for {args.ticker}")
        print(f"  Profile: {snapshot.profile_used}")
        print(f"  Metrics: {len(snapshot.metrics_included or [])}")

        if snapshot.warnings:
            print(f"  Warnings: {len(snapshot.warnings)}")
            if args.verbose:
                for warning in snapshot.warnings:
                    print(f"    - {warning}")

        # Display summary if requested
        if args.show:
            summary = service.get_metrics_summary(args.ticker)
            if summary:
                print("\nMetrics Summary:")
                print(json.dumps(summary['metrics'], indent=2))

        return 0

    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Failed to calculate metrics: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_calculate_watchlist(args: argparse.Namespace) -> int:
    """Calculate metrics for all tickers in a watchlist."""
    store = get_store(args.data_dir)
    service = MetricsService(json_store=store)

    try:
        summary = service.calculate_for_watchlist(
            watchlist_name=args.watchlist,
            max_tickers=args.max_tickers,
            save_history=not args.no_history
        )

        print("Metrics calculation complete. Summary:")
        print(json.dumps(summary, indent=2))
        return 0

    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Failed to calculate metrics: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_show_metrics(args: argparse.Namespace) -> int:
    """Display calculated metrics for a ticker."""
    store = get_store(args.data_dir)
    service = MetricsService(json_store=store)

    try:
        summary = service.get_metrics_summary(
            ticker=args.ticker,
            timestamp=args.timestamp
        )

        if not summary:
            print(f"No metrics found for {args.ticker}", file=sys.stderr)
            return 1

        print(json.dumps(summary, indent=2))
        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_list_history(args: argparse.Namespace) -> int:
    """List historical metric snapshots for a ticker."""
    store = get_store(args.data_dir)

    try:
        history = store.list_metrics_history(args.ticker)
        if not history:
            print(f"No metrics history found for {args.ticker}")
            return 0

        print(f"Metrics history for {args.ticker}:")
        for timestamp in history:
            print(f"  {timestamp}")

        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for metrics calculation."""
    parser = argparse.ArgumentParser(
        description="Calculate and view investment metrics."
    )
    parser.add_argument(
        "--data-dir",
        help="Base directory for JsonStore (default: ./data)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Calculate for single ticker
    calc_ticker_parser = subparsers.add_parser(
        "calculate",
        help="Calculate metrics for a single ticker"
    )
    calc_ticker_parser.add_argument(
        "ticker",
        help="Stock ticker symbol"
    )
    calc_ticker_parser.add_argument(
        "--profile",
        default="buffett_core",
        help="Metrics profile to use (default: buffett_core)"
    )
    calc_ticker_parser.add_argument(
        "--no-history",
        action="store_true",
        help="Skip writing historical snapshots"
    )
    calc_ticker_parser.add_argument(
        "--show",
        action="store_true",
        help="Display calculated metrics after calculation"
    )
    calc_ticker_parser.set_defaults(func=cmd_calculate_ticker)

    # Calculate for watchlist
    calc_watchlist_parser = subparsers.add_parser(
        "calculate-watchlist",
        help="Calculate metrics for all tickers in a watchlist"
    )
    calc_watchlist_parser.add_argument(
        "--watchlist",
        default="default",
        help="Watchlist name to process (default: default)"
    )
    calc_watchlist_parser.add_argument(
        "--max-tickers",
        type=int,
        help="Limit the number of tickers processed"
    )
    calc_watchlist_parser.add_argument(
        "--no-history",
        action="store_true",
        help="Skip writing historical snapshots"
    )
    calc_watchlist_parser.set_defaults(func=cmd_calculate_watchlist)

    # Show metrics
    show_parser = subparsers.add_parser(
        "show",
        help="Display calculated metrics for a ticker"
    )
    show_parser.add_argument(
        "ticker",
        help="Stock ticker symbol"
    )
    show_parser.add_argument(
        "--timestamp",
        help="Specific timestamp to view (default: latest)"
    )
    show_parser.set_defaults(func=cmd_show_metrics)

    # List history
    history_parser = subparsers.add_parser(
        "history",
        help="List historical metric snapshots"
    )
    history_parser.add_argument(
        "ticker",
        help="Stock ticker symbol"
    )
    history_parser.set_defaults(func=cmd_list_history)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
