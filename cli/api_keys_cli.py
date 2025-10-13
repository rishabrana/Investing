"""
Command-line utilities for managing API keys stored via JsonStore.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from storage.json_store import (
    API_ENV_MAP,
    SUPPORTED_PROVIDERS,
    JsonStore,
    normalize_provider_name,
)


def _supported_provider_rows():
    rows = []
    for provider in SUPPORTED_PROVIDERS:
        env_var = API_ENV_MAP.get(provider)
        rows.append((provider, env_var))
    return rows


def _print_supported_providers():
    print("Supported providers:")
    for provider, env_var in _supported_provider_rows():
        env_text = env_var if env_var else "(no env var)"
        print(f"- {provider}  (env: {env_text})")


def _mask(value: str) -> str:
    value = value or ""
    if len(value) <= 4:
        return "***"
    return f"{value[:3]}***{value[-2:]}"


def get_store(data_dir: Optional[str]) -> JsonStore:
    """Instantiate JsonStore with optional custom data directory."""
    if data_dir:
        return JsonStore(data_dir=data_dir)
    return JsonStore()


def cmd_list(args: argparse.Namespace) -> int:
    """List all stored API keys (masked)."""
    store = get_store(args.data_dir)
    stored = store.load_api_keys()

    print(f"{'Provider':<28} {'Status':<10} {'Source':<20} {'Value':<15}")
    print("-" * 80)

    missing = []
    for provider, env_var in _supported_provider_rows():
        env_value = os.getenv(env_var) if env_var else None
        stored_value = stored.get(provider)

        if env_var is None:  # no key required
            status = "N/A"
            source = "n/a"
            display = ""
        elif env_value:
            status = "SET"
            source = f"env:{env_var}"
            display = _mask(env_value)
        elif stored_value:
            status = "SET"
            source = "stored"
            display = _mask(stored_value)
        else:
            status = "MISSING"
            source = env_var or "stored"
            display = ""
            if env_var:
                missing.append(provider)

        print(f"{provider:<28} {status:<10} {source:<20} {display:<15}")

    if missing:
        print("\nMissing API keys detected for:")
        for provider in missing:
            env_var = API_ENV_MAP.get(provider)
            hint = f"Set {env_var}" if env_var else "Use cli.api_keys_cli add"
            print(f"- {provider} ({hint})")

    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add or update an API key."""
    store = get_store(args.data_dir)
    try:
        store.save_api_key(args.provider, args.key)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        _print_supported_providers()
        return 1

    canonical = normalize_provider_name(args.provider) or args.provider
    print(f"Stored API key for {canonical}.")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a stored API key."""
    store = get_store(args.data_dir)
    removed = store.delete_api_key(args.provider)
    if removed:
        canonical = normalize_provider_name(args.provider) or args.provider
        print(f"Removed API key for {canonical}.")
        return 0
    print(f"No API key found for {args.provider}.")
    _print_supported_providers()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage stored API keys.")
    parser.add_argument(
        "--data-dir",
        help="Base directory for JsonStore (default: ./data)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List stored API keys")
    list_parser.set_defaults(func=cmd_list)

    add_parser = subparsers.add_parser("add", help="Add or update an API key")
    add_parser.add_argument(
        "provider",
        help="Provider identifier (see supported list, e.g., polygon.io)",
    )
    add_parser.add_argument("key", help="API key value")
    add_parser.set_defaults(func=cmd_add)

    remove_parser = subparsers.add_parser("remove", help="Delete an API key")
    remove_parser.add_argument("provider", help="Provider identifier to remove")
    remove_parser.set_defaults(func=cmd_remove)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
