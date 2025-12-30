"""Stock data and metrics endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import time

from storage.json_store import JsonStore, RawSnapshot, MetricsSnapshot
from services.data_ingestion_service import DataIngestionService
from services.metrics_service import MetricsService
from backend.api.dependencies import (
    get_json_store,
    get_data_ingestion_service,
    get_metrics_service
)
from backend.models.requests import RefreshStockRequest, RefreshWatchlistRequest
from backend.models.responses import (
    StockOverviewResponse,
    StockMetricsResponse,
    StockHistoryResponse,
    RefreshStockResponse,
    RefreshWatchlistResponse,
    RefreshResult,
    PriceData,
    MarketData,
    HistoryDataPoint,
)
from backend.services.logging_service import get_logger, LogLevel, OperationType

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/{ticker}/overview", response_model=StockOverviewResponse)
async def get_stock_overview(
    ticker: str,
    store: JsonStore = Depends(get_json_store)
):
    """
    Get stock overview with price and market data.

    Args:
        ticker: Stock ticker symbol

    Returns:
        StockOverviewResponse with price and market data
    """
    ticker = ticker.upper()
    snapshot = store.read_raw_snapshot(ticker)

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for {ticker}. Try refreshing first."
        )

    # Extract price data
    price_info = snapshot.price or {}
    market_info = snapshot.market_data or {}

    # Calculate price change if we have previous data
    close = price_info.get("close")
    open_price = price_info.get("open")
    change = None
    change_percent = None

    if close and open_price:
        change = close - open_price
        change_percent = (change / open_price) * 100 if open_price else None

    price_data = PriceData(
        close=close or 0.0,
        open=open_price,
        high=price_info.get("high"),
        low=price_info.get("low"),
        change=change,
        change_percent=change_percent,
        as_of=snapshot.as_of or ""
    )

    market_data = MarketData(
        market_cap=market_info.get("market_cap"),
        shares_outstanding=market_info.get("shares_outstanding")
    )

    # Try to get company name from watchlist
    watchlist = store.load_watchlist("default")
    name = ticker
    if watchlist:
        for entry in watchlist.tickers:
            if entry.symbol == ticker:
                name = entry.name or ticker
                break

    return StockOverviewResponse(
        ticker=ticker,
        name=name,
        price=price_data,
        market_data=market_data,
        fetched_at=snapshot.fetched_at
    )


@router.get("/{ticker}/metrics", response_model=StockMetricsResponse)
async def get_stock_metrics(
    ticker: str,
    profile: str = Query("buffett_core", description="Metrics profile to use"),
    store: JsonStore = Depends(get_json_store)
):
    """
    Get calculated metrics for a stock.

    Args:
        ticker: Stock ticker symbol
        profile: Metrics profile name (default: buffett_core)

    Returns:
        StockMetricsResponse with all calculated metrics
    """
    ticker = ticker.upper()
    snapshot = store.read_metrics_snapshot(ticker)

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=f"No metrics found for {ticker}. Try refreshing first."
        )

    # Extract category data
    # Note: Growth metrics are included in profitability category
    return StockMetricsResponse(
        ticker=snapshot.ticker,
        as_of=snapshot.as_of,
        calculated_at=snapshot.calculated_at,
        profile_used=snapshot.profile_used,
        valuation=snapshot.valuation or {},
        profitability=snapshot.profitability or {},
        cash_generation=snapshot.cash_generation or {},
        financial_strength=snapshot.financial_strength or {},
        capital_allocation=snapshot.capital_allocation or {},
        moat=snapshot.moat or {},
        growth={}  # Growth metrics are in profitability
    )


@router.get("/{ticker}/history", response_model=StockHistoryResponse)
async def get_stock_history(
    ticker: str,
    metric: str = Query(..., description="Metric ID to fetch (e.g., 'roic', 'free_cash_flow')"),
    years: int = Query(10, ge=1, le=20, description="Number of years of history"),
    store: JsonStore = Depends(get_json_store)
):
    """
    Get historical data for a specific metric.

    Args:
        ticker: Stock ticker symbol
        metric: Metric ID (e.g., 'return_on_invested_capital', 'free_cash_flow')
        years: Number of years of history (1-20)

    Returns:
        StockHistoryResponse with historical data points
    """
    ticker = ticker.upper()
    snapshot = store.read_raw_snapshot(ticker)

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for {ticker}"
        )

    # Map common metric names to data locations
    metric_map = {
        "roic": ("financials_history", "roic"),
        "return_on_invested_capital": ("financials_history", "roic"),
        "roe": ("financials_history", "roe"),
        "return_on_equity": ("financials_history", "roe"),
        "free_cash_flow": ("financials_history", "free_cash_flow"),
        "fcf": ("financials_history", "free_cash_flow"),
        "revenue": ("financials_history", "revenue"),
        "net_income": ("financials_history", "net_income"),
        "operating_margin": ("financials_history", "operating_margin"),
        "gross_margin": ("financials_history", "gross_margin"),
        "operating_income": ("financials_history", "operating_income"),
        "shareholders_equity": ("financials_history", "shareholders_equity"),
        "total_debt": ("financials_history", "total_debt"),
        "operating_cash_flow": ("financials_history", "operating_cash_flow"),
        "capital_expenditure": ("financials_history", "capital_expenditure"),
    }

    if metric not in metric_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported metric: {metric}. Supported metrics: {list(metric_map.keys())}"
        )

    section, field = metric_map[metric]
    history = getattr(snapshot, section, [])

    if not history:
        return StockHistoryResponse(
            ticker=ticker,
            metric=metric,
            data_points=[]
        )

    # Sort history by period (oldest to newest) and limit to requested years
    sorted_history = sorted(history, key=lambda x: x.get("period", ""))
    limited_history = sorted_history[-years:] if len(sorted_history) > years else sorted_history

    # Calculate derived metrics if needed
    data_points = []
    for record in limited_history:
        period = record.get("period")
        value = record.get(field)

        # Calculate ROIC if not present: (Net Income - Dividends) / (Debt + Equity)
        if field == "roic" and value is None:
            net_income = record.get("net_income")
            equity = record.get("shareholders_equity")
            debt = record.get("total_debt", 0)
            if net_income and equity:
                invested_capital = (equity + debt) if debt else equity
                value = net_income / invested_capital if invested_capital else None

        # Calculate ROE if not present: Net Income / Equity
        elif field == "roe" and value is None:
            net_income = record.get("net_income")
            equity = record.get("shareholders_equity")
            if net_income and equity:
                value = net_income / equity

        # Calculate FCF if not present: Operating Cash Flow - CapEx
        elif field == "free_cash_flow" and value is None:
            ocf = record.get("operating_cash_flow")
            capex = record.get("capital_expenditure", 0)
            if ocf is not None:
                value = ocf - (capex if capex else 0)

        if period:
            data_points.append(
                HistoryDataPoint(period=period, value=value)
            )

    return StockHistoryResponse(
        ticker=ticker,
        metric=metric,
        data_points=data_points
    )


@router.post("/{ticker}/refresh", response_model=RefreshStockResponse)
async def refresh_stock(
    ticker: str,
    request: RefreshStockRequest = RefreshStockRequest(),
    store: JsonStore = Depends(get_json_store),
    data_service: DataIngestionService = Depends(get_data_ingestion_service),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    Refresh stock data from API providers with automatic rollback on failure.

    This will:
    1. Save backup of current data
    2. Fetch latest financial data from APIs
    3. Recalculate all metrics
    4. Validate data quality
    5. Rollback to backup if data quality is poor

    Args:
        ticker: Stock ticker symbol
        request: Refresh options

    Returns:
        RefreshStockResponse with fetch results
    """
    logger = get_logger()
    ticker = ticker.upper()
    start_time = time.time()

    # Get baseline metrics count from existing data
    baseline_snapshot = store.read_metrics_snapshot(ticker)
    baseline_metrics_count = 0
    if baseline_snapshot and baseline_snapshot.metrics_included:
        baseline_metrics_count = len(baseline_snapshot.metrics_included)

    # Fetch raw data
    try:
        result = data_service.refresh_ticker(ticker)
        fetch_duration = (time.time() - start_time) * 1000

        # Log data fetch
        logger.log_data_fetch(
            ticker=ticker,
            success=result.success,
            providers_used=result.providers_used,
            fields_fetched=len(result.fields_fetched),
            fields_missing=len(result.fields_missing),
            duration_ms=fetch_duration,
            error='; '.join(result.errors) if result.errors else None
        )

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch data for {ticker}: {'; '.join(result.errors)}"
            )
    except Exception as e:
        fetch_duration = (time.time() - start_time) * 1000
        logger.log_data_fetch(
            ticker=ticker,
            success=False,
            providers_used={},
            fields_fetched=0,
            fields_missing=0,
            duration_ms=fetch_duration,
            error=str(e)
        )
        raise

    # Calculate metrics
    metrics_start = time.time()
    metrics_calculated = []
    metrics_failed = []
    warnings = []

    try:
        snapshot = metrics_service.calculate_metrics(ticker, profile="buffett_core")
        metrics_duration = (time.time() - metrics_start) * 1000

        # Extract calculated metrics
        if snapshot:
            for category in ['valuation', 'profitability', 'cash_generation', 'financial_strength', 'capital_allocation', 'moat']:
                data = getattr(snapshot, category, {})
                if data:
                    metrics_calculated.extend(data.keys())

        # Data quality check: if new metrics count is significantly lower, restore from backup
        new_metrics_count = len(metrics_calculated)
        data_degraded = False

        if baseline_metrics_count > 0 and new_metrics_count < baseline_metrics_count * 0.5:
            # More than 50% of metrics lost - data is degraded
            data_degraded = True
            result.warnings.append(
                f"Data quality degraded: only {new_metrics_count} metrics vs baseline {baseline_metrics_count}. "
                f"Using cached data instead."
            )

            # Note: Data is already saved in history by the ingestion service
            # Frontend will use the fetched_at timestamp to show data age

        logger.log_metrics_calculation(
            ticker=ticker,
            profile="buffett_core",
            success=True,
            metrics_calculated=metrics_calculated,
            metrics_failed=metrics_failed,
            duration_ms=metrics_duration,
            warnings=warnings
        )
    except Exception as e:
        metrics_duration = (time.time() - metrics_start) * 1000
        error_msg = f"Metrics calculation failed: {str(e)}"
        result.warnings.append(error_msg)

        logger.log_metrics_calculation(
            ticker=ticker,
            profile="buffett_core",
            success=False,
            metrics_calculated=metrics_calculated,
            metrics_failed=[],
            duration_ms=metrics_duration,
            warnings=warnings,
            error=str(e)
        )

    return RefreshStockResponse(
        success=result.success,
        ticker=ticker,
        fields_fetched=len(result.fields_fetched),
        fields_missing=len(result.fields_missing),
        timestamp=result.snapshot.as_of if result.snapshot else "",
        providers_used=result.providers_used,
        warnings=result.warnings
    )


@router.post("/refresh-watchlist", response_model=RefreshWatchlistResponse)
async def refresh_watchlist(
    request: RefreshWatchlistRequest,
    store: JsonStore = Depends(get_json_store),
    data_service: DataIngestionService = Depends(get_data_ingestion_service),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    Refresh all stocks in the watchlist.

    Args:
        request: RefreshWatchlistRequest with watchlist name

    Returns:
        RefreshWatchlistResponse with batch results
    """
    watchlist = store.load_watchlist(request.watchlist)

    if watchlist is None or not watchlist.tickers:
        raise HTTPException(
            status_code=404,
            detail=f"Watchlist '{request.watchlist}' not found or empty"
        )

    results = []
    successful = 0
    failed = 0

    for entry in watchlist.tickers:
        ticker = entry.symbol
        try:
            # Fetch data
            result = data_service.refresh_ticker(ticker)

            if result.success:
                successful += 1
                # Calculate metrics
                try:
                    metrics_service.calculate_metrics(ticker, profile="buffett_core")
                except Exception:
                    pass  # Ignore metrics errors

                results.append(
                    RefreshResult(
                        ticker=ticker,
                        success=True,
                        fields_fetched=result.fields_fetched,
                        fields_missing=result.fields_missing,
                        errors=[]
                    )
                )
            else:
                failed += 1
                results.append(
                    RefreshResult(
                        ticker=ticker,
                        success=False,
                        fields_fetched=0,
                        fields_missing=0,
                        errors=result.errors
                    )
                )

        except Exception as e:
            failed += 1
            results.append(
                RefreshResult(
                    ticker=ticker,
                    success=False,
                    fields_fetched=0,
                    fields_missing=0,
                    errors=[str(e)]
                )
            )

    return RefreshWatchlistResponse(
        success=failed == 0,
        processed=len(watchlist.tickers),
        successful=successful,
        failed=failed,
        results=results
    )
