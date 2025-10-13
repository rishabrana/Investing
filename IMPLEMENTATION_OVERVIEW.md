## Implementation Overview

This document provides an overview of the extracted implementation files from the technical specification.

---

## Architecture Summary

```
Watchlist (YAML) → DataIngestionService → DataSourceRouter → API Clients
                           ↓                       ↓
                      Normalizer              Rate Limiter
                           ↓
                      JsonStore (Raw Data)
                           ↓
                   MetricsService (future)
                           ↓
                      JsonStore (Metrics Data)
```

---

## Module Organization

### 1. Storage Layer (`storage/`)

#### `storage/json_store.py`
**Purpose**: Local JSON-based storage with time series support

**Key Classes**:
- `RawSnapshot`: Raw data from APIs (NOT computed metrics)
- `MetricsSnapshot`: Computed metrics (derived from raw data)
- `SourceMetadata`: Tracks which provider provided each field
- `JsonStore`: Handles read/write operations

**Directory Structure**:
```
data/
  raw/
    AAPL/
      latest.json              # Most recent raw snapshot
      history/
        2025-10-12T10-00-00Z.json  # Historical snapshots
  metrics/
    AAPL/
      latest.json              # Most recent metrics
      history/
        2025-10-12T10-30-00Z.json  # Historical metrics
  logs/
    fetch_state.json          # Progress tracking
```

**Key Features**:
- **Separation of concerns**: Raw API data never mixed with computed metrics
- **Time series support**: Maintains history for both raw and metrics data
- **Atomic writes**: Uses temp file + rename to prevent corruption
- **Source attribution**: Tracks which provider supplied each field

**Example Usage**:
```python
from storage import JsonStore, create_raw_snapshot

# Initialize store
store = JsonStore(data_dir='./data')

# Create and save raw snapshot
snapshot = create_raw_snapshot(
    ticker='AAPL',
    as_of='2023-09-30',
    price={'close': 175.43},
    financials={'revenue': 383285000000, 'net_income': 96995000000},
    market_data={'market_cap': 2740000000000}
)

store.write_raw_snapshot(snapshot, save_history=True)

# Read latest snapshot
latest = store.read_raw_snapshot('AAPL')
print(f"Latest data as of: {latest.as_of}")

# List historical snapshots
history = store.list_raw_history('AAPL')
print(f"Historical snapshots: {history}")
```

---

### 2. Data Ingestion Layer (`services/`)

#### `services/data_ingestion.py`
**Purpose**: Orchestrates data fetching from multiple API sources

**Key Classes**:
- `DataIngestionService`: Main orchestrator
- `Watchlist`: Represents list of stocks to track
- `WatchlistEntry`: Single ticker with metadata
- `FetchResult`: Result of fetching data for one ticker

**Workflow**:
1. Load watchlist (from YAML)
2. For each ticker:
   - Determine required fields
   - Route to APIs via DataSourceRouter
   - Normalize responses
   - Store raw data in JsonStore
3. Track progress for resume capability

**Key Features**:
- **Stateless**: Doesn't store state between runs
- **Resume capability**: Can continue interrupted runs
- **Progress tracking**: Saves state to allow resume
- **Batch processing**: Processes entire watchlist
- **No metrics calculation**: Only fetches and stores raw data

**Example Usage**:
```python
from services import DataIngestionService, load_watchlist
from storage.json_store import JsonStore
from services import DataSourceRouter, Normalizer
from storage import JsonStore

# Initialize components
store = JsonStore('./data')
router = DataSourceRouter('config/data_source_mapping.yaml')
normalizer = Normalizer()

service = DataIngestionService(
    json_store=store,
    data_source_router=router,
    normalizer=normalizer,
    period='annual'
)

# Load watchlist
store = JsonStore()
watchlist = load_watchlist(store)

# Refresh all tickers
summary = service.refresh_watchlist(watchlist, resume=True)

print(f"Successful: {summary['successful']}/{summary['processed']}")
print(f"Providers used: {summary['providers_used']}")
```

**Watchlist YAML Format**:
```yaml
default_metrics_profile: buffett_core

tickers:
  - symbol: AAPL
    name: Apple Inc
    notes: Consumer tech moat
    metrics_profile: wide_moat_focus

  - symbol: BRK.B
    name: Berkshire Hathaway
    notes: Buffett own company

  - symbol: KO
    name: Coca-Cola
    notes: Classic value play
```

---

#### `services/data_source_router.py`
**Purpose**: Routes field requests to appropriate API providers

**Key Classes**:
- `DataSourceRouter`: Main router
- `FieldMapping`: Configuration for a single field
- `FetchResponse`: Response with fetched data + metadata

**Key Features**:
- **Configuration-driven**: Reads `data_source_mapping.yaml`
- **Intelligent batching**: Groups fields by endpoint to minimize API calls
- **Automatic fallback**: Falls back to secondary/tertiary providers
- **Source attribution**: Tracks which provider supplied each field
- **Caching**: Reuses responses within a run

**How It Works**:
1. Load field mappings from YAML
2. Plan optimal API call batches:
   - Group fields by provider
   - Group by endpoint within provider
   - Minimize HTTP round-trips
3. Execute calls through provider clients
4. Handle fallbacks for missing fields
5. Return aggregated response

**Example**:
```python
from services import DataSourceRouter

router = DataSourceRouter('config/data_source_mapping.yaml')

# Fetch specific fields
response = router.fetch_fields(
    ticker='AAPL',
    fields={
        'price.close',
        'financials.revenue',
        'financials.net_income',
        'assumptions.beta'
    },
    period='annual'
)

print(f"Fields fetched: {len(response.fields_fetched)}")
print(f"Fields missing: {len(response.fields_missing)}")
print(f"Providers used: {response.providers_used}")
```

---

#### `services/normalizer.py`
**Purpose**: Converts provider-specific data to standard format

**Key Features**:
- **Field name translation**: Polygon's `equity` → `shareholders_equity`
- **Data type conversion**: Ensures consistent types
- **Derived field calculation**: Calculates FCF, margins, etc.
- **Provider-agnostic**: Handles multiple provider formats

**Field Mappings**:
- **Polygon.io**: `equity`, `revenues`, `net_income_loss` → standard names
- **Alpha Vantage**: `retainedEarnings`, `interestExpense` → standard names
- **FMP**: `depreciationAndAmortization`, `ebitda` → standard names
- **Yahoo Finance**: `"Interest Expense"`, `"Depreciation"` → standard names

**Derived Fields**:
- `free_cash_flow = operating_cash_flow - capital_expenditure`
- `pre_tax_income = net_income + income_tax_expense`
- `gross_margin = gross_profit / revenue`
- `operating_margin = operating_income / revenue`
- `net_margin = net_income / revenue`

**Example**:
```python
from services import Normalizer
from storage import SourceMetadata

normalizer = Normalizer()

# Raw data from Polygon (with Polygon field names)
raw_data = {
    'financials': {
        'revenues': 383285000000,
        'net_income_loss': 96995000000,
        'equity': 62497000000
    }
}

source_metadata = {
    'financials.revenue': SourceMetadata(
        provider='polygon.io',
        timestamp='2025-10-12T10:00:00Z',
        endpoint='/vX/reference/financials'
    )
}

# Normalize to standard format
normalized = normalizer.normalize(
    ticker='AAPL',
    raw_data=raw_data,
    source_metadata=source_metadata
)

# Now uses standard field names
print(normalized['financials']['revenue'])  # 383285000000
print(normalized['financials']['net_income'])  # 96995000000
print(normalized['financials']['shareholders_equity'])  # 62497000000
```

---

## Data Separation Strategy

### Raw Data vs. Computed Metrics

**Critical Design Principle**: Raw API data and computed metrics are NEVER mixed.

#### Raw Data (`data/raw/{ticker}/latest.json`)
Contains ONLY data fetched from APIs:
- Price data (OHLC)
- Financial statements (balance sheet, income, cash flow)
- Market data (market cap, shares outstanding)
- Assumptions from APIs (beta, risk-free rate, market risk premium)
- Source metadata (which provider supplied each field)
- Raw API payloads (for debugging)

**Never contains**: Calculated metrics like ROIC, ROE, margin of safety, etc.

#### Computed Metrics (`data/metrics/{ticker}/latest.json`)
Contains ONLY calculated metrics:
- Valuation metrics (P/E, P/B, EV/EBITDA, margin of safety)
- Profitability metrics (ROIC, ROE, margins)
- Cash generation metrics (FCF growth, owner earnings)
- Financial strength metrics (debt ratios, interest coverage)
- Moat indicators
- Notes and warnings from calculations

**Never contains**: Raw API data

### Why Separate?

1. **Data Integrity**: Raw data unchanged, can recalculate metrics anytime
2. **Auditability**: Can trace every field back to its source
3. **Flexibility**: Can change metric calculations without re-fetching data
4. **Efficiency**: Don't need to fetch data every time you calculate metrics
5. **Clarity**: Clear separation of concerns

---

## Time Series Support

Both raw data and metrics support time series storage:

```python
# Latest snapshot
latest = store.read_raw_snapshot('AAPL')

# Specific historical snapshot
historical = store.read_raw_snapshot('AAPL', timestamp='2025-01-15T10-00-00Z')

# List all historical snapshots
history = store.list_raw_history('AAPL')
# Returns: ['2025-01-15T10-00-00Z', '2025-02-15T10-00-00Z', ...]
```

This enables:
- Tracking how data changes over time
- Comparing current vs historical values
- Analyzing trends
- Audit trails

---

## Next Steps

### What's Implemented ✅
- JsonStore with raw/metrics separation
- DataIngestionService orchestration
- DataSourceRouter with batching logic
- Normalizer with field translation
- Time series support
- Progress tracking

### What's Next 🚧
1. **API Clients** (not yet implemented):
   - `clients/polygon_client.py`
   - `clients/fmp_client.py`
   - `clients/alpha_vantage_client.py`
   - `clients/finnhub_client.py`
   - `clients/yahoo_client.py`

2. **Rate Limiter** (referenced but not implemented):
   - Token bucket algorithm
   - Per-provider limits
   - Coordinated throttling

3. **MetricsService** (future):
   - Reads raw data from JsonStore
   - Calculates metrics based on profiles
   - Writes metrics to JsonStore

4. **CLI Tools** (future):
   - `cli/data_fetch.py` - Batch data refresh
   - `cli/metrics_cli.py` - Calculate and display metrics

---

## Configuration Files

The implementation depends on these configuration files:

1. **`config/data_source_mapping.yaml`** ✅ (already exists)
   - Maps fields to API providers
   - Defines fallback chain
   - Specifies endpoints

2. **`config/metric_catalog.yaml`** ✅ (already exists)
   - Defines all metrics
   - Technical formulas
   - Required data points

3. **`config/metrics_config.yaml`** 🚧 (needs creation)
   - Metric profiles (buffett_core, wide_moat_focus, etc.)
   - Profile inheritance
   - Metric groupings

4. **`watchlist.yaml`** 🚧 (user-created)
   - List of tickers to track
   - Per-ticker settings
   - Default profile

---

## Testing Strategy

### Unit Tests Needed
- `test_json_store.py`: Test CRUD operations, atomic writes, history
- `test_normalizer.py`: Test field translation, derived calculations
- `test_data_source_router.py`: Test batching logic, fallbacks
- `test_data_ingestion.py`: Test orchestration, progress tracking

### Integration Tests Needed
- End-to-end: Watchlist → Fetch → Store → Retrieve
- Multi-provider fallback scenarios
- Resume capability

### Test Data
- Mock API responses for each provider
- Sample watchlists
- Expected normalized outputs

---

## Summary

This implementation provides a solid foundation for the data acquisition layer:

✅ **Clean separation** between raw data and computed metrics
✅ **Time series support** for tracking changes over time
✅ **Source attribution** to know where every field came from
✅ **Resume capability** for handling interruptions
✅ **Configuration-driven** design for flexibility
✅ **Provider-agnostic** normalization

The next phase will implement the actual API clients and metrics calculation service.
