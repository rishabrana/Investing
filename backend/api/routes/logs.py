"""Logs and monitoring endpoints."""

from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import datetime

from backend.services.logging_service import get_logger, OperationType, LogLevel

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/recent-errors")
async def get_recent_errors(
    operation_type: Optional[str] = Query(None, description="Filter by operation type (API_CALL, METRICS_CALCULATION, DATA_FETCH)"),
    hours: int = Query(24, ge=1, le=168, description="Look back this many hours"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries")
):
    """
    Get recent error logs for troubleshooting.

    Args:
        operation_type: Filter by operation type
        hours: Look back period in hours
        limit: Maximum number of results

    Returns:
        List of recent error log entries
    """
    logger = get_logger()

    op_type = None
    if operation_type:
        try:
            op_type = OperationType[operation_type]
        except KeyError:
            pass

    errors = logger.get_recent_errors(
        operation_type=op_type,
        hours=hours,
        limit=limit
    )

    return {
        "count": len(errors),
        "hours": hours,
        "operation_type": operation_type,
        "errors": errors
    }


@router.get("/stats")
async def get_log_stats():
    """
    Get statistics about recent logs.

    Returns:
        Summary statistics of logs
    """
    logger = get_logger()

    # Get errors from last 24 hours
    all_errors = logger.get_recent_errors(hours=24, limit=1000)

    # Count by operation type
    by_operation = {}
    by_ticker = {}
    by_provider = {}

    for error in all_errors:
        op = error.get("operation_type", "UNKNOWN")
        by_operation[op] = by_operation.get(op, 0) + 1

        ticker = error.get("ticker")
        if ticker:
            by_ticker[ticker] = by_ticker.get(ticker, 0) + 1

        provider = error.get("provider")
        if provider:
            by_provider[provider] = by_provider.get(provider, 0) + 1

    return {
        "period": "last_24_hours",
        "total_errors": len(all_errors),
        "by_operation_type": by_operation,
        "by_ticker": by_ticker,
        "by_provider": by_provider,
        "most_recent": all_errors[0] if all_errors else None
    }
