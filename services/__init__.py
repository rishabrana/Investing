"""
Services module for data ingestion and processing.

This module contains:
- DataIngestionService: Orchestrates data fetching from APIs
- DataSourceRouter: Routes requests to appropriate providers
- Normalizer: Converts provider-specific data to standard format
- MetricsService: Calculates investment metrics from raw data
"""

from services.data_ingestion import (
    DataIngestionService,
    FetchResult,
    Watchlist,
    WatchlistEntry,
    create_sample_watchlist,
    load_watchlist,
)
from services.data_source_router import DataSourceRouter, validate_mapping
from services.field_mapping import FieldMapping
from services.fetch_response import FetchResponse
from services.normalizer import Normalizer, validate_normalized_data
from services.metrics_service import MetricsService
from services.metric_calculator import MetricCalculator, MetricResult

__all__ = [
    # Data Ingestion
    'DataIngestionService',
    'Watchlist',
    'WatchlistEntry',
    'FetchResult',
    'load_watchlist',
    'create_sample_watchlist',

    # Data Source Router
    'DataSourceRouter',
    'FieldMapping',
    'FetchResponse',
    'validate_mapping',

    # Normalizer
    'Normalizer',
    'validate_normalized_data',

    # Metrics
    'MetricsService',
    'MetricCalculator',
    'MetricResult',
]
