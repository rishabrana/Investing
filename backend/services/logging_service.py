"""
Logging service for tracking API calls and metrics calculations.

This service provides structured logging for all external API calls and internal
metric calculations, enabling troubleshooting and monitoring of data quality.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class LogLevel(Enum):
    """Log levels for different types of events."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class OperationType(Enum):
    """Types of operations being logged."""
    API_CALL = "API_CALL"
    METRICS_CALCULATION = "METRICS_CALCULATION"
    DATA_FETCH = "DATA_FETCH"
    DATA_VALIDATION = "DATA_VALIDATION"


class TimeSeriesLogger:
    """
    Time-series logger for tracking API calls and metrics calculations.

    Logs are stored in JSON format with timestamps for easy analysis.
    """

    def __init__(self, log_dir: str = "./logs"):
        """
        Initialize the time-series logger.

        Args:
            log_dir: Directory where log files will be stored
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set up Python logging for console output
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("InvestmentAnalysis")

    def _get_log_file(self, operation_type: OperationType) -> Path:
        """
        Get the log file path for a specific operation type.

        Args:
            operation_type: Type of operation being logged

        Returns:
            Path to the log file
        """
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{operation_type.value.lower()}_{today}.jsonl"
        return self.log_dir / filename

    def log_event(
        self,
        operation_type: OperationType,
        level: LogLevel,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        ticker: Optional[str] = None,
        provider: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error: Optional[str] = None
    ):
        """
        Log an event with structured data.

        Args:
            operation_type: Type of operation
            level: Log level
            message: Human-readable message
            details: Additional structured data
            ticker: Stock ticker (if applicable)
            provider: API provider (if applicable)
            duration_ms: Operation duration in milliseconds
            error: Error message (if applicable)
        """
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "operation_type": operation_type.value,
            "level": level.value,
            "message": message,
        }

        if ticker:
            log_entry["ticker"] = ticker
        if provider:
            log_entry["provider"] = provider
        if duration_ms is not None:
            log_entry["duration_ms"] = duration_ms
        if error:
            log_entry["error"] = error
        if details:
            log_entry["details"] = details

        # Write to JSONL file (one JSON object per line)
        log_file = self._get_log_file(operation_type)
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Also log to console
        log_msg = f"[{operation_type.value}] {message}"
        if ticker:
            log_msg += f" (ticker: {ticker})"
        if provider:
            log_msg += f" (provider: {provider})"

        if level == LogLevel.ERROR:
            self.logger.error(log_msg)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)

    def log_api_call(
        self,
        provider: str,
        endpoint: str,
        ticker: str,
        success: bool,
        duration_ms: float,
        status_code: Optional[int] = None,
        fields_requested: Optional[List[str]] = None,
        fields_received: Optional[List[str]] = None,
        error: Optional[str] = None
    ):
        """
        Log an external API call.

        Args:
            provider: API provider name (e.g., 'polygon.io')
            endpoint: API endpoint called
            ticker: Stock ticker
            success: Whether the call succeeded
            duration_ms: Call duration in milliseconds
            status_code: HTTP status code
            fields_requested: Fields requested from API
            fields_received: Fields successfully received
            error: Error message if failed
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        message = f"API call to {provider} {endpoint}"

        details = {
            "endpoint": endpoint,
            "status_code": status_code,
            "fields_requested": fields_requested or [],
            "fields_received": fields_received or [],
            "success": success
        }

        self.log_event(
            operation_type=OperationType.API_CALL,
            level=level,
            message=message,
            details=details,
            ticker=ticker,
            provider=provider,
            duration_ms=duration_ms,
            error=error
        )

    def log_metrics_calculation(
        self,
        ticker: str,
        profile: str,
        success: bool,
        metrics_calculated: List[str],
        metrics_failed: List[str],
        duration_ms: float,
        warnings: Optional[List[str]] = None,
        error: Optional[str] = None
    ):
        """
        Log a metrics calculation event.

        Args:
            ticker: Stock ticker
            profile: Metrics profile used
            success: Whether calculation succeeded
            metrics_calculated: List of successfully calculated metrics
            metrics_failed: List of metrics that failed
            duration_ms: Calculation duration in milliseconds
            warnings: List of warnings generated
            error: Error message if failed
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        if warnings and success:
            level = LogLevel.WARNING

        message = f"Metrics calculation for {ticker} using {profile} profile"

        details = {
            "profile": profile,
            "metrics_calculated": metrics_calculated,
            "metrics_failed": metrics_failed,
            "metrics_count": len(metrics_calculated),
            "failed_count": len(metrics_failed),
            "warnings": warnings or [],
            "success": success
        }

        self.log_event(
            operation_type=OperationType.METRICS_CALCULATION,
            level=level,
            message=message,
            details=details,
            ticker=ticker,
            duration_ms=duration_ms,
            error=error
        )

    def log_data_fetch(
        self,
        ticker: str,
        success: bool,
        providers_used: Dict[str, int],
        fields_fetched: int,
        fields_missing: int,
        duration_ms: float,
        error: Optional[str] = None
    ):
        """
        Log a complete data fetch operation (may involve multiple API calls).

        Args:
            ticker: Stock ticker
            success: Whether fetch succeeded
            providers_used: Dict of provider names to number of calls
            fields_fetched: Number of fields successfully fetched
            fields_missing: Number of fields that couldn't be fetched
            duration_ms: Total fetch duration in milliseconds
            error: Error message if failed
        """
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        if fields_missing > 0 and success:
            level = LogLevel.WARNING

        message = f"Data fetch for {ticker}"

        details = {
            "providers_used": providers_used,
            "fields_fetched": fields_fetched,
            "fields_missing": fields_missing,
            "success": success
        }

        self.log_event(
            operation_type=OperationType.DATA_FETCH,
            level=level,
            message=message,
            details=details,
            ticker=ticker,
            duration_ms=duration_ms,
            error=error
        )

    def get_recent_errors(
        self,
        operation_type: Optional[OperationType] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent error logs.

        Args:
            operation_type: Filter by operation type (None for all)
            hours: Look back this many hours
            limit: Maximum number of entries to return

        Returns:
            List of error log entries
        """
        errors = []
        cutoff_time = datetime.now().timestamp() - (hours * 3600)

        # Determine which log files to search
        if operation_type:
            log_files = [self._get_log_file(operation_type)]
        else:
            log_files = [self._get_log_file(op) for op in OperationType]

        for log_file in log_files:
            if not log_file.exists():
                continue

            with open(log_file, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("level") == "ERROR":
                            entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
                            if entry_time >= cutoff_time:
                                errors.append(entry)
                    except json.JSONDecodeError:
                        continue

        # Sort by timestamp (newest first) and limit
        errors.sort(key=lambda x: x["timestamp"], reverse=True)
        return errors[:limit]


# Global logger instance
_logger: Optional[TimeSeriesLogger] = None


def get_logger() -> TimeSeriesLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = TimeSeriesLogger()
    return _logger
