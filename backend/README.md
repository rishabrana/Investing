# Investment Analysis API - Backend

FastAPI-based REST API server for the Investment Analysis web application.

## Features

- **Watchlist Management**: Add, remove, and list stocks in your watchlist
- **Stock Data**: Fetch price, market data, and financial metrics
- **Historical Data**: Retrieve historical trends for key metrics
- **Data Refresh**: Update stock data from external APIs
- **Shared Logic**: Reuses existing CLI services for consistency

## Installation

```bash
# From the backend directory
pip install -r requirements.txt
```

## Running the Server

### Development Mode (with auto-reload)

```bash
# From the project root directory
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the main.py directly:

```bash
python -m backend.api.main
```

### Production Mode

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### Health & Status

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/ready` - Readiness check with dependency status

### Watchlist

- `GET /api/v1/watchlist` - Get all tickers in watchlist
- `POST /api/v1/watchlist/add` - Add a ticker to watchlist
- `DELETE /api/v1/watchlist/{symbol}` - Remove ticker from watchlist
- `POST /api/v1/watchlist/validate` - Validate ticker symbol

### Stock Data

- `GET /api/v1/stocks/{ticker}/overview` - Get stock overview (price, market data)
- `GET /api/v1/stocks/{ticker}/metrics` - Get calculated metrics
- `GET /api/v1/stocks/{ticker}/history` - Get historical data for a metric
- `POST /api/v1/stocks/{ticker}/refresh` - Refresh data for a stock
- `POST /api/v1/stocks/refresh-watchlist` - Refresh all stocks in watchlist

## Example Requests

### Add a ticker to watchlist

```bash
curl -X POST "http://localhost:8000/api/v1/watchlist/add" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "notes": "Great business"
  }'
```

### Get stock metrics

```bash
curl "http://localhost:8000/api/v1/stocks/AAPL/metrics"
```

### Get historical ROE data

```bash
curl "http://localhost:8000/api/v1/stocks/AAPL/history?metric=roe&years=10"
```

### Refresh stock data

```bash
curl -X POST "http://localhost:8000/api/v1/stocks/AAPL/refresh" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

## Architecture

The API server follows these principles:

1. **Dependency Injection**: Services are injected via FastAPI's `Depends()`
2. **Shared Business Logic**: Reuses existing `storage`, `services`, and `clients` modules
3. **Type Safety**: Pydantic models for request/response validation
4. **CORS Enabled**: Allows requests from React dev server
5. **Error Handling**: Proper HTTP status codes and error messages

## Project Structure

```
backend/
├── api/
│   ├── main.py           # FastAPI app entry point
│   ├── dependencies.py   # Dependency injection
│   └── routes/
│       ├── watchlist.py  # Watchlist endpoints
│       ├── stocks.py     # Stock data endpoints
│       └── health.py     # Health check endpoints
├── models/
│   ├── requests.py       # Pydantic request models
│   └── responses.py      # Pydantic response models
├── tests/
│   └── (test files)
├── requirements.txt
└── README.md
```

## Development

### Adding a New Endpoint

1. Define Pydantic models in `models/requests.py` and `models/responses.py`
2. Create route in `api/routes/` directory
3. Register router in `api/main.py`
4. Test with Swagger UI at `/api/docs`

### Running Tests

```bash
pytest tests/
```

## Environment Variables

The API uses the same environment variables as the CLI:

- `POLYGON_API_KEY` - Polygon.io API key
- `ALPHA_VANTAGE_API_KEY` - Alpha Vantage API key

These are read from the `.env` file in the project root.

## CORS Configuration

By default, CORS is enabled for:
- http://localhost:3000 (Create React App)
- http://localhost:5173 (Vite)

To modify allowed origins, edit `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-url.com"],
    ...
)
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`, make sure you're running from the project root:

```bash
# Wrong: cd backend && python api/main.py
# Correct: python -m backend.api.main
```

### Port Already in Use

If port 8000 is busy:

```bash
uvicorn api.main:app --port 8001
```

### API Key Errors

Check that your `.env` file exists in the project root with:

```
POLYGON_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```
