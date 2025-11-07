"""
JsonStore - Local JSON-based storage for stock data with time series support.

This module provides a file-based storage system that separates:
1. Raw API data (fetched from external sources)
2. Computed metrics (calculated from raw data)

Data is organized per stock with time series support for historical snapshots.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field

import yaml

# Mapping between provider identifiers and expected environment variables.
API_ENV_MAP: Dict[str, Optional[str]] = {
    "polygon.io": "POLYGON_API_KEY",
    "financial_modeling_prep": "FMP_API_KEY",
    "alpha_vantage": "ALPHA_VANTAGE_API_KEY",
    "finnhub.io": "FINNHUB_API_KEY",
    "yahoo_finance": None,  # library-based/no API key required
}

# Provider name aliases to canonical identifiers used internally.
_PROVIDER_ALIASES: Dict[str, str] = {
    "polygon": "polygon.io",
    "polygonio": "polygon.io",
    "polygon.io": "polygon.io",
    "financial_modeling_prep": "financial_modeling_prep",
    "financialmodelingprep": "financial_modeling_prep",
    "financial-modeling-prep": "financial_modeling_prep",
    "alpha_vantage": "alpha_vantage",
    "alphavantage": "alpha_vantage",
    "alpha-vantage": "alpha_vantage",
    "finnhub": "finnhub.io",
    "finnhub.io": "finnhub.io",
}

SUPPORTED_PROVIDERS: Tuple[str, ...] = tuple(API_ENV_MAP.keys())


def normalize_provider_name(provider: Optional[str]) -> Optional[str]:
    """Normalize user-supplied provider names to canonical identifiers."""
    if not provider:
        return None
    key = provider.strip().lower().replace(" ", "")
    return _PROVIDER_ALIASES.get(key)


@dataclass
class SourceMetadata:
    """Metadata about data source and fetch time."""
    provider: str
    timestamp: str
    endpoint: Optional[str] = None


@dataclass
class WatchlistEntry:
    """Represents a single ticker in the watchlist."""
    symbol: str
    name: Optional[str] = None
    notes: Optional[str] = None
    metrics_profile: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.symbol = self.symbol.upper()
        if not self.name:
            self.name = self.symbol

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            'symbol': self.symbol,
            'name': self.name,
        }
        if self.notes is not None:
            data['notes'] = self.notes
        if self.metrics_profile is not None:
            data['metrics_profile'] = self.metrics_profile
        data.update(self.custom_fields)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WatchlistEntry':
        extras = {
            k: v for k, v in data.items()
            if k not in {'symbol', 'name', 'notes', 'metrics_profile'}
        }
        return cls(
            symbol=data['symbol'],
            name=data.get('name'),
            notes=data.get('notes'),
            metrics_profile=data.get('metrics_profile'),
            custom_fields=extras
        )


@dataclass
class Watchlist:
    """Represents a collection of tickers with shared defaults."""
    tickers: List[WatchlistEntry]
    default_metrics_profile: str = "buffett_core"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            'default_metrics_profile': self.default_metrics_profile,
            'tickers': [entry.to_dict() for entry in self.tickers],
        }
        data.update(self.metadata)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Watchlist':
        tickers = [
            WatchlistEntry.from_dict(entry)
            for entry in data.get('tickers', [])
        ]
        metadata = {
            k: v for k, v in data.items()
            if k not in {'tickers', 'default_metrics_profile'}
        }
        return cls(
            tickers=tickers,
            default_metrics_profile=data.get(
                'default_metrics_profile', 'buffett_core'
            ),
            metadata=metadata
        )

    @classmethod
    def from_yaml(cls, filepath: str) -> 'Watchlist':
        """Load a watchlist definition from a YAML file."""
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data or {})


@dataclass
class RawSnapshot:
    """Raw data snapshot from API sources.

    This contains ONLY data fetched from APIs, with no computed metrics.
    """
    ticker: str
    as_of: str  # Date this data represents (e.g., fiscal period end)
    fetched_at: str  # When this data was actually fetched

    # Price data
    price: Optional[Dict[str, Any]] = None

    # Financial statements (raw from APIs)
    financials: Optional[Dict[str, Any]] = None

    # Market data
    market_data: Optional[Dict[str, Any]] = None

    # Cash flow data
    cash_flow: Optional[Dict[str, Any]] = None

    # Assumptions fetched from APIs (beta, risk-free rate, etc.)
    assumptions: Optional[Dict[str, Any]] = None

    # Historical data for time-series metrics
    financials_history: Optional[List[Dict[str, Any]]] = None
    market_data_history: Optional[List[Dict[str, Any]]] = None
    cash_flow_history: Optional[List[Dict[str, Any]]] = None
    metrics_history: Optional[List[Dict[str, Any]]] = None
    projections: Optional[Dict[str, Any]] = None  # For DCF calculations

    # Source attribution - tracks which provider provided each field
    source_metadata: Optional[Dict[str, SourceMetadata]] = None

    # Raw API payloads (for debugging/auditing)
    raw_payloads: Optional[Dict[str, Any]] = None


@dataclass
class MetricsSnapshot:
    """Computed metrics snapshot.

    This contains ONLY computed/calculated metrics, derived from raw data.
    Stored separately from raw data.
    """
    ticker: str
    as_of: str
    calculated_at: str
    profile_used: str

    # Computed metrics organized by category
    valuation: Optional[Dict[str, Any]] = None
    profitability: Optional[Dict[str, Any]] = None
    cash_generation: Optional[Dict[str, Any]] = None
    financial_strength: Optional[Dict[str, Any]] = None
    capital_allocation: Optional[Dict[str, Any]] = None
    moat: Optional[Dict[str, Any]] = None

    # Metrics included in this calculation
    metrics_included: Optional[List[str]] = None

    # Notes and warnings from calculations
    notes: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class JsonStore:
    """
    Local JSON-based storage with time series support.

    Directory structure:
    ${DATA_DIR}/
        raw/
            {ticker}/
                latest.json              # Most recent raw snapshot
                history/
                    {timestamp}.json     # Historical snapshots
        metrics/
            {ticker}/
                latest.json              # Most recent metrics
                history/
                    {timestamp}.json     # Historical metrics
        logs/
            fetch_state.json            # Progress tracking for data fetch

    Separation of concerns:
    - Raw data (from APIs) stored in raw/
    - Computed metrics stored in metrics/
    - Never mixed together
    """

    def __init__(self, data_dir: str = "./data"):
        """
        Initialize JsonStore.

        Args:
            data_dir: Base directory for all data storage
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.metrics_dir = self.data_dir / "metrics"
        self.logs_dir = self.data_dir / "logs"
        self.credentials_dir = self.logs_dir / "credentials"

        # Create directory structure
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directory structure."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

    def _get_ticker_raw_dir(self, ticker: str) -> Path:
        """Get raw data directory for a ticker."""
        path = self.raw_dir / ticker.upper()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _get_ticker_metrics_dir(self, ticker: str) -> Path:
        """Get metrics directory for a ticker."""
        path = self.metrics_dir / ticker.upper()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _get_watchlist_dir(self) -> Path:
        """Get directory where watchlists are stored."""
        path = self.data_dir / "watchlists"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _atomic_write(self, filepath: Path, data: Dict[str, Any]):
        """
        Write JSON data atomically using temp file + rename.

        This prevents corruption from interrupted writes.
        """
        # Write to temp file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent,
            prefix=f".{filepath.name}.",
            suffix=".tmp"
        )

        try:
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            # Atomic rename
            os.replace(temp_path, filepath)
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    # ===== RAW DATA METHODS =====

    def write_raw_snapshot(
        self,
        snapshot: RawSnapshot,
        save_history: bool = True
    ):
        """
        Write raw API data snapshot.

        Args:
            snapshot: Raw data snapshot from APIs
            save_history: If True, also save to history/
        """
        ticker_dir = self._get_ticker_raw_dir(snapshot.ticker)

        # Convert dataclass to dict
        data = asdict(snapshot)

        # Write latest snapshot
        latest_path = ticker_dir / "latest.json"
        self._atomic_write(latest_path, data)

        # Optionally save to history
        if save_history:
            history_dir = ticker_dir / "history"
            history_dir.mkdir(exist_ok=True)

            timestamp = snapshot.fetched_at.replace(':', '-')
            history_path = history_dir / f"{timestamp}.json"
            self._atomic_write(history_path, data)

    def _has_meaningful_data(self, obj: Any) -> bool:
        """
        Recursively check if an object contains meaningful data.

        Returns False if obj is None, empty dict, empty list, or nested structure with only None values.
        """
        if obj is None:
            return False
        if isinstance(obj, dict):
            if not obj:  # Empty dict
                return False
            # Check if any value in dict has meaningful data
            return any(self._has_meaningful_data(v) for v in obj.values())
        if isinstance(obj, list):
            if not obj:  # Empty list
                return False
            # Check if any item in list has meaningful data
            return any(self._has_meaningful_data(item) for item in obj)
        # Primitive value (number, string, bool) - considered meaningful
        return True

    def _is_raw_snapshot_empty(self, snapshot: RawSnapshot) -> bool:
        """
        Check if a raw snapshot has no meaningful data.

        A snapshot is considered empty if all data fields contain no meaningful values
        (only None, empty dicts/lists, or nested structures with only None values).
        """
        data_fields = [
            snapshot.price,
            snapshot.financials,
            snapshot.market_data,
            snapshot.cash_flow,
            snapshot.assumptions,
            snapshot.financials_history,
            snapshot.market_data_history,
            snapshot.cash_flow_history,
            snapshot.metrics_history,
            snapshot.projections
        ]

        # Check if any field has meaningful data
        for field in data_fields:
            if self._has_meaningful_data(field):
                return False

        return True

    def read_raw_snapshot(
        self,
        ticker: str,
        timestamp: Optional[str] = None,
        fallback_to_previous: bool = True
    ) -> Optional[RawSnapshot]:
        """
        Read raw data snapshot with fallback to previous day if empty.

        Args:
            ticker: Stock ticker symbol
            timestamp: Optional specific timestamp. If None, reads latest.
            fallback_to_previous: If True, fallback to most recent non-empty snapshot

        Returns:
            RawSnapshot or None if not found
        """
        ticker_dir = self._get_ticker_raw_dir(ticker)

        if timestamp:
            # Read from history
            history_path = ticker_dir / "history" / f"{timestamp}.json"
            if not history_path.exists():
                return None
            filepath = history_path
        else:
            # Read latest
            filepath = ticker_dir / "latest.json"
            if not filepath.exists():
                return None

        with open(filepath, 'r') as f:
            data = json.load(f)

        snapshot = RawSnapshot(**data)

        # If snapshot is empty and fallback is enabled, try to find previous non-empty snapshot
        if fallback_to_previous and self._is_raw_snapshot_empty(snapshot):
            # Get all historical snapshots sorted by date (newest first)
            history_timestamps = self.list_raw_history(ticker)
            history_timestamps.reverse()  # Most recent first

            for hist_timestamp in history_timestamps:
                try:
                    # Read historical snapshot
                    history_path = ticker_dir / "history" / f"{hist_timestamp}.json"
                    if history_path.exists():
                        with open(history_path, 'r') as f:
                            hist_data = json.load(f)

                        hist_snapshot = RawSnapshot(**hist_data)

                        # If this snapshot has data, use it
                        if not self._is_raw_snapshot_empty(hist_snapshot):
                            return hist_snapshot
                except Exception:
                    # Skip invalid snapshots
                    continue

        return snapshot

    def list_raw_history(self, ticker: str) -> List[str]:
        """
        List all historical raw snapshots for a ticker.

        Returns:
            List of timestamps (filenames without .json)
        """
        ticker_dir = self._get_ticker_raw_dir(ticker)
        history_dir = ticker_dir / "history"

        if not history_dir.exists():
            return []

        timestamps = [
            f.stem for f in history_dir.glob("*.json")
        ]
        return sorted(timestamps)

    # ===== METRICS DATA METHODS =====

    def write_metrics_snapshot(
        self,
        snapshot: MetricsSnapshot,
        save_history: bool = True
    ):
        """
        Write computed metrics snapshot.

        Args:
            snapshot: Computed metrics snapshot
            save_history: If True, also save to history/
        """
        ticker_dir = self._get_ticker_metrics_dir(snapshot.ticker)

        # Convert dataclass to dict
        data = asdict(snapshot)

        # Write latest snapshot
        latest_path = ticker_dir / "latest.json"
        self._atomic_write(latest_path, data)

        # Optionally save to history
        if save_history:
            history_dir = ticker_dir / "history"
            history_dir.mkdir(exist_ok=True)

            timestamp = snapshot.calculated_at.replace(':', '-')
            history_path = history_dir / f"{timestamp}.json"
            self._atomic_write(history_path, data)

    def _is_metrics_snapshot_empty(self, snapshot: MetricsSnapshot) -> bool:
        """
        Check if a metrics snapshot has no meaningful data.

        A snapshot is considered empty if all metric categories contain no meaningful values
        (only None, empty dicts, or nested structures with only None values).
        """
        metric_fields = [
            snapshot.valuation,
            snapshot.profitability,
            snapshot.cash_generation,
            snapshot.financial_strength,
            snapshot.capital_allocation,
            snapshot.moat
        ]

        # Check if any field has meaningful data
        for field in metric_fields:
            if self._has_meaningful_data(field):
                return False

        return True

    def read_metrics_snapshot(
        self,
        ticker: str,
        timestamp: Optional[str] = None,
        fallback_to_previous: bool = True
    ) -> Optional[MetricsSnapshot]:
        """
        Read computed metrics snapshot with fallback to previous day if empty.

        Args:
            ticker: Stock ticker symbol
            timestamp: Optional specific timestamp. If None, reads latest.
            fallback_to_previous: If True, fallback to most recent non-empty snapshot

        Returns:
            MetricsSnapshot or None if not found
        """
        ticker_dir = self._get_ticker_metrics_dir(ticker)

        if timestamp:
            # Read from history
            history_path = ticker_dir / "history" / f"{timestamp}.json"
            if not history_path.exists():
                return None
            filepath = history_path
        else:
            # Read latest
            filepath = ticker_dir / "latest.json"
            if not filepath.exists():
                return None

        with open(filepath, 'r') as f:
            data = json.load(f)

        snapshot = MetricsSnapshot(**data)

        # If snapshot is empty and fallback is enabled, try to find previous non-empty snapshot
        if fallback_to_previous and self._is_metrics_snapshot_empty(snapshot):
            # Get all historical snapshots sorted by date (newest first)
            history_timestamps = self.list_metrics_history(ticker)
            history_timestamps.reverse()  # Most recent first

            for hist_timestamp in history_timestamps:
                try:
                    # Read historical snapshot
                    history_path = ticker_dir / "history" / f"{hist_timestamp}.json"
                    if history_path.exists():
                        with open(history_path, 'r') as f:
                            hist_data = json.load(f)

                        hist_snapshot = MetricsSnapshot(**hist_data)

                        # If this snapshot has data, use it
                        if not self._is_metrics_snapshot_empty(hist_snapshot):
                            return hist_snapshot
                except Exception:
                    # Skip invalid snapshots
                    continue

        return snapshot

    def list_metrics_history(self, ticker: str) -> List[str]:
        """
        List all historical metrics snapshots for a ticker.

        Returns:
            List of timestamps (filenames without .json)
        """
        ticker_dir = self._get_ticker_metrics_dir(ticker)
        history_dir = ticker_dir / "history"

        if not history_dir.exists():
            return []

        timestamps = [
            f.stem for f in history_dir.glob("*.json")
        ]
        return sorted(timestamps)

    # ===== WATCHLIST METHODS =====

    def save_watchlist(
        self,
        watchlist: Watchlist,
        name: str = "default"
    ):
        """
        Persist a watchlist definition.

        Args:
            watchlist: Watchlist instance to save
            name: Friendly name for the watchlist file
        """
        watchlist_dir = self._get_watchlist_dir()
        filepath = watchlist_dir / f"{name}.json"
        data = watchlist.to_dict()
        self._atomic_write(filepath, data)

    def load_watchlist(
        self,
        name: str = "default"
    ) -> Optional[Watchlist]:
        """
        Load a watchlist definition.

        Args:
            name: Friendly name of the watchlist file

        Returns:
            Watchlist or None if not found
        """
        watchlist_dir = self._get_watchlist_dir()
        filepath = watchlist_dir / f"{name}.json"
        if not filepath.exists():
            return None

        with open(filepath, 'r') as file:
            data = json.load(file)

        return Watchlist.from_dict(data)

    def list_watchlists(self) -> List[str]:
        """
        List all stored watchlists.

        Returns:
            List of watchlist names (without extension)
        """
        watchlist_dir = self._get_watchlist_dir()
        return sorted(
            f.stem for f in watchlist_dir.glob("*.json") if f.is_file()
        )

    # ===== GENERAL METHODS =====

    def list_tickers(self) -> List[str]:
        """
        List all tickers with stored data.

        Returns:
            List of ticker symbols
        """
        raw_tickers = set(
            d.name for d in self.raw_dir.iterdir() if d.is_dir()
        )
        metrics_tickers = set(
            d.name for d in self.metrics_dir.iterdir() if d.is_dir()
        )

        return sorted(raw_tickers | metrics_tickers)

    def delete_ticker_data(
        self,
        ticker: str,
        raw_only: bool = False,
        metrics_only: bool = False
    ):
        """
        Delete all data for a ticker.

        Args:
            ticker: Stock ticker symbol
            raw_only: If True, delete only raw data
            metrics_only: If True, delete only metrics data
        """
        import shutil

        ticker = ticker.upper()

        if not metrics_only:
            raw_dir = self.raw_dir / ticker
            if raw_dir.exists():
                shutil.rmtree(raw_dir)

        if not raw_only:
            metrics_dir = self.metrics_dir / ticker
            if metrics_dir.exists():
                shutil.rmtree(metrics_dir)

    # ===== FETCH STATE MANAGEMENT =====

    def save_fetch_state(self, state: Dict[str, Any]):
        """
        Save fetch progress state for resume capability.

        Args:
            state: Dictionary with fetch progress info
        """
        state_path = self.logs_dir / "fetch_state.json"
        self._atomic_write(state_path, state)

    def load_fetch_state(self) -> Optional[Dict[str, Any]]:
        """
        Load fetch progress state.

        Returns:
            Fetch state dict or None if not found
        """
        state_path = self.logs_dir / "fetch_state.json"
        if not state_path.exists():
            return None

        with open(state_path, 'r') as f:
            return json.load(f)

    def clear_fetch_state(self):
        """Clear fetch progress state."""
        state_path = self.logs_dir / "fetch_state.json"
        if state_path.exists():
            state_path.unlink()

    # ===== API KEY MANAGEMENT =====

    def _get_credentials_file(self) -> Path:
        """Path to the credentials JSON file."""
        return self.credentials_dir / "api_keys.json"

    def load_api_keys(self) -> Dict[str, str]:
        """
        Load stored API keys from disk.

        Returns:
            Dict mapping provider name -> API key.
        """
        filepath = self._get_credentials_file()
        if not filepath.exists():
            legacy_dir = self.logs_dir / "credentials"
            legacy_file = legacy_dir / "api_keys.json"
            if legacy_file.exists():
                with open(legacy_file, "r") as fh:
                    legacy_data = json.load(fh)
                filepath.parent.mkdir(parents=True, exist_ok=True)
                self._atomic_write(filepath, legacy_data)
                try:
                    legacy_file.unlink()
                except OSError:
                    pass
            else:
                return {}
        with open(filepath, "r") as fh:
            raw_data = json.load(fh)

        normalized: Dict[str, str] = {}
        changed = False
        for provider, key in raw_data.items():
            canonical = normalize_provider_name(provider)
            if canonical:
                normalized[canonical] = key
                if canonical != provider:
                    changed = True
            else:
                normalized[provider] = key

        if changed:
            self._atomic_write(filepath, normalized)

        return normalized

    def save_api_key(self, provider: str, api_key: str):
        """
        Add or update an API key for the specified provider.

        Args:
            provider: Provider identifier (e.g., 'polygon.io')
            api_key: API key string
        """
        canonical = normalize_provider_name(provider)
        if not canonical:
            raise ValueError(
                f"Unsupported provider '{provider}'. Supported providers: "
                f"{', '.join(SUPPORTED_PROVIDERS)}"
            )
        provider = canonical
        data = self.load_api_keys()
        data[provider] = api_key
        self._atomic_write(self._get_credentials_file(), data)

    def delete_api_key(self, provider: str) -> bool:
        """
        Remove the API key for the specified provider if it exists.

        Returns:
            True if a key was removed; False otherwise.
        """
        canonical = normalize_provider_name(provider)
        if not canonical:
            return False
        provider = canonical
        data = self.load_api_keys()
        if provider not in data:
            return False
        del data[provider]
        self._atomic_write(self._get_credentials_file(), data)
        return True

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Resolve an API key for a provider, checking environment variables first.

        Args:
            provider: Provider identifier (e.g., 'polygon.io').

        Returns:
            API key string or None if not available.
        """
        canonical = normalize_provider_name(provider)
        if not canonical:
            return None

        env_var = API_ENV_MAP.get(canonical)
        if env_var:
            env_value = os.getenv(env_var)
            if env_value and env_value.strip():
                return env_value.strip()

        stored = self.load_api_keys()
        key = stored.get(canonical)
        if key and isinstance(key, str):
            key = key.strip()
        return key or None


# ===== HELPER FUNCTIONS =====

def create_raw_snapshot(
    ticker: str,
    as_of: str,
    price: Optional[Dict] = None,
    financials: Optional[Dict] = None,
    market_data: Optional[Dict] = None,
    cash_flow: Optional[Dict] = None,
    assumptions: Optional[Dict] = None,
    financials_history: Optional[List[Dict]] = None,
    market_data_history: Optional[List[Dict]] = None,
    cash_flow_history: Optional[List[Dict]] = None,
    metrics_history: Optional[List[Dict]] = None,
    projections: Optional[Dict] = None,
    source_metadata: Optional[Dict] = None,
    raw_payloads: Optional[Dict] = None
) -> RawSnapshot:
    """
    Helper to create a RawSnapshot with current timestamp.

    Args:
        ticker: Stock ticker symbol
        as_of: Date this data represents
        price: Price data
        financials: Financial statement data
        market_data: Market data (market cap, etc.)
        cash_flow: Cash flow data
        assumptions: Assumptions data (beta, risk-free rate, etc.)
        financials_history: Historical financial data
        market_data_history: Historical market data
        cash_flow_history: Historical cash flow data
        metrics_history: Historical metrics data
        projections: Projected cash flows for DCF
        source_metadata: Source attribution
        raw_payloads: Raw API responses

    Returns:
        RawSnapshot instance
    """
    return RawSnapshot(
        ticker=ticker.upper(),
        as_of=as_of,
        fetched_at=datetime.utcnow().isoformat(),
        price=price,
        financials=financials,
        market_data=market_data,
        cash_flow=cash_flow,
        assumptions=assumptions,
        financials_history=financials_history,
        market_data_history=market_data_history,
        cash_flow_history=cash_flow_history,
        metrics_history=metrics_history,
        projections=projections,
        source_metadata=source_metadata,
        raw_payloads=raw_payloads
    )


def create_metrics_snapshot(
    ticker: str,
    as_of: str,
    profile_used: str,
    valuation: Optional[Dict] = None,
    profitability: Optional[Dict] = None,
    cash_generation: Optional[Dict] = None,
    financial_strength: Optional[Dict] = None,
    capital_allocation: Optional[Dict] = None,
    moat: Optional[Dict] = None,
    metrics_included: Optional[List[str]] = None,
    notes: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None
) -> MetricsSnapshot:
    """
    Helper to create a MetricsSnapshot with current timestamp.

    Args:
        ticker: Stock ticker symbol
        as_of: Date this data represents
        profile_used: Metrics profile used for calculations
        valuation: Valuation metrics
        profitability: Profitability metrics
        cash_generation: Cash generation metrics
        financial_strength: Financial strength metrics
        capital_allocation: Capital allocation metrics
        moat: Economic moat metrics
        metrics_included: List of metric IDs included
        notes: Calculation notes
        warnings: Warnings from calculations

    Returns:
        MetricsSnapshot instance
    """
    return MetricsSnapshot(
        ticker=ticker.upper(),
        as_of=as_of,
        calculated_at=datetime.utcnow().isoformat(),
        profile_used=profile_used,
        valuation=valuation,
        profitability=profitability,
        cash_generation=cash_generation,
        financial_strength=financial_strength,
        capital_allocation=capital_allocation,
        moat=moat,
        metrics_included=metrics_included or [],
        notes=notes,
        warnings=warnings
    )


def load_watchlist_from_store(
    store: Optional[JsonStore] = None,
    name: str = "default"
) -> Watchlist:
    """
    Convenience helper to load a watchlist using JsonStore.

    Args:
        store: Existing JsonStore instance. If None, a default one is created.
        name: Watchlist name to load.

    Returns:
        Watchlist instance.
    """
    store = store or JsonStore()
    watchlist = store.load_watchlist(name=name)
    if watchlist is None:
        raise FileNotFoundError(
            f"Watchlist '{name}' not found in {store.data_dir}/watchlists"
        )
    return watchlist


def create_sample_watchlist(
    store: Optional[JsonStore] = None,
    name: str = "sample"
) -> Watchlist:
    """
    Convenience helper to create and persist a sample watchlist.

    Args:
        store: Existing JsonStore instance. If None, a default one is created.
        name: Watchlist name to use when saving.

    Returns:
        The created Watchlist instance.
    """
    store = store or JsonStore()

    sample = Watchlist(
        tickers=[
            WatchlistEntry(
                symbol="AAPL",
                name="Apple Inc",
                notes="Consumer tech moat",
                metrics_profile="wide_moat_focus"
            ),
            WatchlistEntry(
                symbol="BRK.B",
                name="Berkshire Hathaway",
                notes="Buffett own company"
            ),
            WatchlistEntry(
                symbol="KO",
                name="Coca-Cola",
                notes="Classic value play"
            )
        ],
        default_metrics_profile="buffett_core"
    )

    store.save_watchlist(sample, name=name)
    return sample
