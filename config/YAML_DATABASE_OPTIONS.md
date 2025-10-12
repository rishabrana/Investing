# YAML-Based Local Database Options for Python

## Overview

There are several lightweight, file-based database solutions for Python that can work with YAML files or provide similar functionality.

---

## 🏆 Best Options for Your Project

### 1. TinyDB with YAML Storage ⭐ RECOMMENDED

**Why it's great:**
- Pure Python, no external dependencies (except PyYAML for YAML storage)
- Document-oriented (perfect for storing financial data)
- Simple query API
- Extensible with custom storage backends
- Active development and well-documented

**Installation:**
```bash
pip install tinydb pyyaml
```

**Custom YAML Storage Implementation:**
```python
from tinydb import TinyDB, Storage
import yaml

class YAMLStorage(Storage):
    """YAML storage for TinyDB"""

    def __init__(self, filename):
        self.filename = filename

    def read(self):
        """Read data from YAML file"""
        try:
            with open(self.filename, 'r') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except FileNotFoundError:
            return {}

    def write(self, data):
        """Write data to YAML file"""
        with open(self.filename, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def close(self):
        """Close storage (nothing to do for files)"""
        pass

# Usage
db = TinyDB('data/stocks.yml', storage=YAMLStorage)

# Insert data
db.insert({
    'ticker': 'AAPL',
    'price': 175.43,
    'beta': 1.23,
    'market_cap': 2800000000000
})

# Query data
from tinydb import Query
Stock = Query()
result = db.search(Stock.ticker == 'AAPL')
print(result)

# Update data
db.update({'price': 176.50}, Stock.ticker == 'AAPL')

# Close
db.close()
```

**Pros:**
- ✅ Easy to use, Pythonic API
- ✅ Query capabilities (search, update, delete)
- ✅ Human-readable YAML files
- ✅ No server required
- ✅ Perfect for small to medium datasets

**Cons:**
- ⚠️ Not suitable for large datasets (1000s+ records)
- ⚠️ No built-in indexing (loads entire file into memory)
- ⚠️ Not thread-safe by default

---

### 2. Plain PyYAML with Custom Logic ⭐ SIMPLEST

**Why consider it:**
- Minimal dependencies (just PyYAML)
- Maximum control
- Perfect for simple use cases

**Installation:**
```bash
pip install pyyaml
```

**Simple Implementation:**
```python
import yaml
from pathlib import Path
from typing import List, Dict, Any

class YAMLDatabase:
    """Simple YAML-based database"""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load data from YAML file"""
        if self.filepath.exists():
            with open(self.filepath, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}

    def _save(self):
        """Save data to YAML file"""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True)

    def insert(self, collection: str, document: Dict[str, Any]):
        """Insert a document into a collection"""
        if collection not in self.data:
            self.data[collection] = []
        self.data[collection].append(document)
        self._save()

    def find(self, collection: str, query: Dict[str, Any] = None) -> List[Dict]:
        """Find documents matching query"""
        if collection not in self.data:
            return []

        items = self.data[collection]

        if query is None:
            return items

        # Simple query matching
        results = []
        for item in items:
            match = all(item.get(key) == value for key, value in query.items())
            if match:
                results.append(item)

        return results

    def update(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]):
        """Update documents matching query"""
        if collection not in self.data:
            return

        for item in self.data[collection]:
            match = all(item.get(key) == value for key, value in query.items())
            if match:
                item.update(update)

        self._save()

    def delete(self, collection: str, query: Dict[str, Any]):
        """Delete documents matching query"""
        if collection not in self.data:
            return

        self.data[collection] = [
            item for item in self.data[collection]
            if not all(item.get(key) == value for key, value in query.items())
        ]
        self._save()

# Usage
db = YAMLDatabase('data/stocks.yml')

# Insert
db.insert('stocks', {
    'ticker': 'AAPL',
    'price': 175.43,
    'beta': 1.23
})

# Find
stocks = db.find('stocks', {'ticker': 'AAPL'})
print(stocks)

# Update
db.update('stocks', {'ticker': 'AAPL'}, {'price': 176.50})

# Delete
db.delete('stocks', {'ticker': 'AAPL'})
```

**Pros:**
- ✅ Extremely simple
- ✅ Full control over data structure
- ✅ Minimal dependencies
- ✅ Human-readable files

**Cons:**
- ⚠️ No advanced query capabilities
- ⚠️ Manual implementation of features
- ⚠️ No indexing

---

### 3. TinyDB with JSON (Default) ⭐ FASTEST

**Why consider it:**
- TinyDB's native storage format
- Faster than YAML
- Same API and features

```python
from tinydb import TinyDB, Query

# Just use JSON storage (default)
db = TinyDB('data/stocks.json')

# Everything else is the same as YAML version
db.insert({'ticker': 'AAPL', 'price': 175.43})
Stock = Query()
result = db.search(Stock.ticker == 'AAPL')
```

**Pros:**
- ✅ Faster than YAML
- ✅ More compact files
- ✅ Default TinyDB storage

**Cons:**
- ⚠️ Less human-readable than YAML
- ⚠️ Harder to manually edit

---

### 4. SQLite with YAML Import/Export

**Why consider it:**
- Best performance for larger datasets
- Built-in to Python (no external dependencies)
- Can export to YAML for human readability

```python
import sqlite3
import yaml

class SQLiteYAMLDB:
    """SQLite database with YAML export/import"""

    def __init__(self, db_file: str):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row

    def create_table(self, table_name: str, schema: Dict[str, str]):
        """Create table from schema"""
        columns = ', '.join(f"{col} {dtype}" for col, dtype in schema.items())
        self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    def insert(self, table: str, data: Dict):
        """Insert data"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.conn.execute(sql, tuple(data.values()))
        self.conn.commit()

    def find(self, table: str, where: Dict = None) -> List[Dict]:
        """Find records"""
        sql = f"SELECT * FROM {table}"
        params = []

        if where:
            conditions = ' AND '.join(f"{k}=?" for k in where.keys())
            sql += f" WHERE {conditions}"
            params = list(where.values())

        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def export_to_yaml(self, yaml_file: str):
        """Export entire database to YAML"""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        data = {}
        for table in tables:
            cursor = self.conn.execute(f"SELECT * FROM {table}")
            data[table] = [dict(row) for row in cursor.fetchall()]

        with open(yaml_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def import_from_yaml(self, yaml_file: str):
        """Import data from YAML"""
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        for table, records in data.items():
            if records:
                # Create table from first record
                first_record = records[0]
                schema = {k: 'TEXT' for k in first_record.keys()}
                self.create_table(table, schema)

                # Insert records
                for record in records:
                    self.insert(table, record)

# Usage
db = SQLiteYAMLDB('data/stocks.db')

# Work with SQL
db.create_table('stocks', {
    'ticker': 'TEXT PRIMARY KEY',
    'price': 'REAL',
    'beta': 'REAL'
})
db.insert('stocks', {'ticker': 'AAPL', 'price': 175.43, 'beta': 1.23})

# Export to YAML for human readability
db.export_to_yaml('data/stocks_backup.yml')

# Import from YAML
db.import_from_yaml('data/stocks_backup.yml')
```

**Pros:**
- ✅ Best performance
- ✅ SQL query capabilities
- ✅ ACID compliance
- ✅ Can export to YAML when needed

**Cons:**
- ⚠️ Not natively YAML (needs conversion)
- ⚠️ More complex setup

---

## 📊 Comparison Table

| Feature | TinyDB + YAML | PyYAML Custom | TinyDB + JSON | SQLite + YAML |
|---------|---------------|---------------|---------------|---------------|
| **Setup Complexity** | Medium | Simple | Simple | Complex |
| **Query Capability** | Good | Basic | Good | Excellent |
| **Performance** | Medium | Slow | Fast | Fastest |
| **Human Readable** | ✅ Yes | ✅ Yes | ⚠️ Partial | ⚠️ With export |
| **File Size** | Large | Large | Medium | Small |
| **Best For** | 100-1000 records | <100 records | 100-10000 records | 10000+ records |
| **Manual Editing** | ✅ Easy | ✅ Easy | ⚠️ Harder | ❌ No |
| **Dependencies** | tinydb, pyyaml | pyyaml only | tinydb only | Built-in |

---

## 🎯 Recommendation for Your Investing Project

### For Configuration/Metadata: **Plain PyYAML**
Use for:
- `metric_catalog.yaml` (already using)
- `data_source_mapping.yaml` (already using)
- App configuration

**Why**: Human-readable, easy to edit manually, version control friendly

### For Cached API Data: **TinyDB with JSON**
Use for:
- Caching stock prices
- Storing fetched financial data
- API response caching

**Why**: Fast, queryable, good for hundreds of stocks

### For Historical Time Series: **SQLite**
Use for:
- Historical price data (years of daily prices)
- Historical financial statements
- Calculated metrics over time

**Why**: Best performance, handles thousands of records easily

---

## 🚀 Implementation Example for Your Project

### Hybrid Approach (Recommended)

```python
# config/database.py
from tinydb import TinyDB, Query
import yaml
from pathlib import Path
import sqlite3

class InvestingDatabase:
    """Hybrid database for investing project"""

    def __init__(self, base_path='data'):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

        # Config/metadata in YAML (human-editable)
        self.config_path = self.base_path / 'config'
        self.config_path.mkdir(exist_ok=True)

        # Cached data in TinyDB JSON (fast, queryable)
        self.cache_db = TinyDB(self.base_path / 'cache.json')

        # Time series in SQLite (best performance)
        self.timeseries_conn = sqlite3.connect(
            self.base_path / 'timeseries.db'
        )
        self._init_timeseries_tables()

    def _init_timeseries_tables(self):
        """Initialize SQLite tables for time series data"""
        self.timeseries_conn.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                ticker TEXT,
                date DATE,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (ticker, date)
            )
        ''')
        self.timeseries_conn.commit()

    # Config methods (YAML)
    def load_config(self, config_name: str) -> dict:
        """Load configuration from YAML"""
        config_file = self.config_path / f'{config_name}.yaml'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def save_config(self, config_name: str, data: dict):
        """Save configuration to YAML"""
        config_file = self.config_path / f'{config_name}.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    # Cache methods (TinyDB)
    def cache_stock_data(self, ticker: str, data: dict):
        """Cache stock data in TinyDB"""
        Stock = Query()
        self.cache_db.upsert(
            {**data, 'ticker': ticker},
            Stock.ticker == ticker
        )

    def get_cached_stock(self, ticker: str) -> dict:
        """Get cached stock data"""
        Stock = Query()
        result = self.cache_db.get(Stock.ticker == ticker)
        return result if result else None

    # Time series methods (SQLite)
    def save_price_history(self, ticker: str, prices: list):
        """Save price history to SQLite"""
        self.timeseries_conn.executemany('''
            INSERT OR REPLACE INTO price_history
            (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            (ticker, p['date'], p['open'], p['high'],
             p['low'], p['close'], p['volume'])
            for p in prices
        ])
        self.timeseries_conn.commit()

    def get_price_history(self, ticker: str, start_date: str = None):
        """Get price history from SQLite"""
        sql = 'SELECT * FROM price_history WHERE ticker = ?'
        params = [ticker]

        if start_date:
            sql += ' AND date >= ?'
            params.append(start_date)

        cursor = self.timeseries_conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

# Usage
db = InvestingDatabase('data')

# Config (YAML)
db.save_config('user_settings', {
    'default_projection_years': 10,
    'terminal_growth_rate': 0.025
})

# Cache (TinyDB JSON)
db.cache_stock_data('AAPL', {
    'price': 175.43,
    'beta': 1.23,
    'last_updated': '2025-10-12'
})

# Time series (SQLite)
db.save_price_history('AAPL', [
    {'date': '2025-10-10', 'open': 174, 'high': 176, 'low': 173, 'close': 175, 'volume': 1000000},
    {'date': '2025-10-11', 'open': 175, 'high': 177, 'low': 174, 'close': 176, 'volume': 1100000},
])
```

---

## 📝 Summary

**For your investing project, I recommend:**

1. **YAML files** (PyYAML) - For config and metric definitions (already doing this ✅)
2. **TinyDB with JSON** - For caching API responses and current stock data
3. **SQLite** - For historical time series data (prices, financials over time)

This gives you:
- ✅ Human-readable configs
- ✅ Fast queryable cache
- ✅ High-performance time series storage
- ✅ All lightweight and local
- ✅ No server required

**Start simple**: Begin with just PyYAML for everything, then add TinyDB when you need querying, then add SQLite when you need performance for large datasets.
