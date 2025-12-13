# Investment Analysis Toolkit

A Buffett-style stock analysis tool with a web interface for tracking fundamentals, calculating investment metrics, and managing your watchlist.

**Local Deployment**: This application runs on your local machine. All data is stored locally and API keys remain private on your computer.

## Quick Start

### 1. Installation

Run the automated installation script:

```bash
./installme.sh
```

This will:
- Check for Python 3 and Node.js
- Install all backend (Python) dependencies
- Install all frontend (React) dependencies
- Create necessary data directories

### 2. Configure API Keys

The app requires API keys to fetch stock data. Add your primary API key:

```bash
source .venv/bin/activate
python -m cli.api_keys_cli add polygon.io YOUR_POLYGON_API_KEY
```

**Required**:
- **polygon.io** - Primary data provider ([Get free key](https://polygon.io/))

**Optional** (for better coverage):
- **alpha_vantage** - Secondary provider ([Get free key](https://www.alphavantage.co/support/#api-key))
- **financial_modeling_prep** - Additional data ([Get free key](https://site.financialmodelingprep.com/developer/docs))
- **finnhub** - Market data ([Get free key](https://finnhub.io/register))

Or add keys through the web interface (Settings → API Keys).

### 3. Start the Application

**Option A - Use the run script (recommended):**
```bash
./runme.sh
```

This starts both backend and frontend servers automatically. Press Ctrl+C to stop both.

**Option B - Manual start (separate terminals):**

Terminal 1 - Backend API:
```bash
PYTHONPATH=$(pwd) python3 -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

**Open your browser**: http://localhost:5173

## Using the Application

1. **Add Stocks**: Click "Add Ticker" in the sidebar
2. **View Analysis**: Select a stock to see Buffett-style metrics:
   - Valuation (P/E, P/B, EV/EBITDA)
   - Profitability (ROIC, ROE, margins)
   - Cash Generation (FCF, owner earnings)
   - Financial Strength (debt ratios, interest coverage)
   - Capital Allocation (dividends, buybacks)
3. **Configure Display**: Use Settings → Section Visibility to customize views

## Command Line Tools (Optional)

The toolkit includes CLI tools for automation:

```bash
# View all commands
source .venv/bin/activate

# Manage watchlists
python -m cli.watchlist_cli list
python -m cli.watchlist_cli add AAPL --company "Apple Inc"

# Fetch data for all watchlist stocks
python -m cli.data_fetch_cli run

# Calculate metrics
python -m cli.metrics_cli calculate-watchlist
python -m cli.metrics_cli show AAPL
```

## Data Storage

All data is stored locally in the `./data` directory:

```
data/
├── raw/           # Raw API data
├── metrics/       # Calculated metrics
├── watchlists/    # Your stock lists
└── credentials/   # API keys (encrypted)
```

## Troubleshooting

**"No data available"**: Make sure you've:
1. Added API keys (Settings → API Keys)
2. Added stocks to your watchlist
3. Backend server is running

**CORS errors**: Ensure both frontend and backend servers are running

**Missing metrics**: Some stocks may have incomplete data. Try adding secondary API providers.

## More Information

- **Detailed Documentation**: See [DETAILED_DOCS.md](DETAILED_DOCS.md)
- **Technical Specs**: See `technical_spec.md`

## Tech Stack

- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Backend**: FastAPI (Python)
- **Data**: Local JSON storage
- **APIs**: Polygon.io, Alpha Vantage, Yahoo Finance, Financial Modeling Prep

---

**Happy Investing!** 📈
