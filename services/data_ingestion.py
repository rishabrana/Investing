"""
Compatibility layer exposing data ingestion classes and helpers.

The actual implementations live in dedicated modules so that each class
resides in its own file, per project style guidelines.
"""

from services.data_ingestion_service import DataIngestionService
from services.fetch_result import FetchResult
from storage.json_store import (
    Watchlist,
    WatchlistEntry,
    create_sample_watchlist as _create_sample_watchlist,
    load_watchlist_from_store,
)


def load_watchlist(store=None, name: str = "default") -> Watchlist:
    """Load a watchlist from the JsonStore."""
    return load_watchlist_from_store(store=store, name=name)


def create_sample_watchlist(store=None, name: str = "sample") -> Watchlist:
    """Create and persist a sample watchlist via JsonStore."""
    return _create_sample_watchlist(store=store, name=name)

__all__ = [
    "DataIngestionService",
    "FetchResult",
    "Watchlist",
    "WatchlistEntry",
    "load_watchlist",
    "create_sample_watchlist",
]
