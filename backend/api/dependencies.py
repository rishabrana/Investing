"""Dependency injection for FastAPI routes."""

import sys
from pathlib import Path

# Add parent directory to path to import existing services
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from storage.json_store import JsonStore
from services.data_ingestion_service import DataIngestionService
from services.metrics_service import MetricsService
from clients.polygon_client import PolygonClient
from clients.alpha_vantage_client import AlphaVantageClient


# Singleton instances (created once per app lifecycle)
_json_store: JsonStore | None = None
_data_ingestion_service: DataIngestionService | None = None
_metrics_service: MetricsService | None = None


def get_json_store() -> JsonStore:
    """Get or create JsonStore instance."""
    global _json_store
    if _json_store is None:
        _json_store = JsonStore(data_dir="./data")
    return _json_store


def get_data_ingestion_service() -> DataIngestionService:
    """Get or create DataIngestionService instance."""
    global _data_ingestion_service
    if _data_ingestion_service is None:
        store = get_json_store()
        _data_ingestion_service = DataIngestionService(
            json_store=store,
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


def get_polygon_client() -> PolygonClient | None:
    """Get PolygonClient for ticker validation."""
    store = get_json_store()
    api_key = store.get_api_key("polygon.io")
    if not api_key:
        return None
    return PolygonClient(api_key)
