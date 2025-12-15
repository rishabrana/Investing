"""Dependency injection for FastAPI routes."""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import existing services
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from storage.json_store import JsonStore
from services.data_ingestion_service import DataIngestionService
from services.metrics_service import MetricsService
from services.data_source_router import DataSourceRouter
from services.normalizer import Normalizer
from clients.polygon_client import PolygonClient
from clients.alpha_vantage_client import AlphaVantageClient
from clients.yahoo_finance_client import YahooFinanceClient


# Singleton instances (created once per app lifecycle)
_json_store: Optional[JsonStore] = None
_data_ingestion_service: Optional[DataIngestionService] = None
_metrics_service: Optional[MetricsService] = None
_data_source_router: Optional[DataSourceRouter] = None
_normalizer: Optional[Normalizer] = None


def get_json_store() -> JsonStore:
    """Get or create JsonStore instance."""
    global _json_store
    if _json_store is None:
        _json_store = JsonStore(data_dir="./data")
    return _json_store


def get_data_source_router() -> DataSourceRouter:
    """Get or create DataSourceRouter instance."""
    global _data_source_router
    if _data_source_router is None:
        store = get_json_store()

        # Initialize API clients
        clients = {}

        # Polygon client
        polygon_api_key = store.get_api_key("polygon.io")
        if polygon_api_key:
            clients["polygon.io"] = PolygonClient(polygon_api_key)

        # Alpha Vantage client
        av_api_key = store.get_api_key("alpha_vantage")
        if av_api_key:
            clients["alpha_vantage"] = AlphaVantageClient(av_api_key)

        # Yahoo Finance client (no API key needed)
        try:
            clients["yahoo_finance"] = YahooFinanceClient()
            print(f"✓ Yahoo Finance client initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize Yahoo Finance client: {e}")

        print(f"Initialized clients: {list(clients.keys())}")

        _data_source_router = DataSourceRouter(
            mapping_path="config/data_source_mapping.yaml",
            clients=clients
        )
    return _data_source_router


def get_normalizer() -> Normalizer:
    """Get or create Normalizer instance."""
    global _normalizer
    if _normalizer is None:
        _normalizer = Normalizer()
    return _normalizer


def get_data_ingestion_service() -> DataIngestionService:
    """Get or create DataIngestionService instance."""
    global _data_ingestion_service
    if _data_ingestion_service is None:
        store = get_json_store()
        router = get_data_source_router()
        normalizer = get_normalizer()
        _data_ingestion_service = DataIngestionService(
            json_store=store,
            data_source_router=router,
            normalizer=normalizer,
            save_history=True
        )
    return _data_ingestion_service


def get_metrics_service() -> MetricsService:
    """Get or create MetricsService instance."""
    global _metrics_service
    if _metrics_service is None:
        store = get_json_store()
        _metrics_service = MetricsService(
            json_store=store,
            metric_catalog_path="config/metric_catalog.yaml"
        )
    return _metrics_service


def get_polygon_client() -> Optional[PolygonClient]:
    """Get PolygonClient for ticker validation."""
    store = get_json_store()
    api_key = store.get_api_key("polygon.io")
    if not api_key:
        return None
    return PolygonClient(api_key)
