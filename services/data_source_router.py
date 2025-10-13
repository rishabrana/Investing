"""
DataSourceRouter - Routes data requests to appropriate API providers.

This router:
1. Loads data source mapping from YAML configuration
2. Plans optimal API call batches to minimize round-trips
3. Routes field requests to appropriate providers (with fallback)
4. Caches responses within a run to avoid duplicate calls
5. Coordinates with rate limiter for throttling

Key features:
- Configuration-driven (reads data_source_mapping.yaml)
- Intelligent batching (groups fields by endpoint)
- Automatic fallback to secondary/tertiary providers
- Source attribution for every field
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

from services.field_mapping import FieldMapping
from services.fetch_response import FetchResponse


logger = logging.getLogger(__name__)


class DataSourceRouter:
    """
    Routes data field requests to appropriate API providers.

    The router is configuration-driven and handles:
    - Loading data source mappings
    - Planning optimal API call batches
    - Executing calls through provider clients
    - Handling fallbacks to secondary providers
    - Caching responses within a run
    """

    def __init__(
        self,
        mapping_path: str = "config/data_source_mapping.yaml",
        clients: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize DataSourceRouter.

        Args:
            mapping_path: Path to data source mapping YAML
            clients: Dictionary of provider clients (e.g., {'polygon.io': PolygonClient()})
        """
        self.mapping_path = Path(mapping_path)
        self.clients = clients or {}

        # Load configuration
        self.mapping = self._load_mapping()
        self.api_priority = self.mapping.get('api_priority', [])

        # Runtime cache (cleared between tickers)
        self._cache: Dict[str, Any] = {}

    def _load_mapping(self) -> Dict[str, Any]:
        """Load data source mapping from YAML."""
        with open(self.mapping_path, 'r') as f:
            return yaml.safe_load(f)

    def get_field_mapping(self, field_id: str) -> Optional[FieldMapping]:
        """
        Get mapping configuration for a field.

        Args:
            field_id: Field identifier (e.g., 'price.close')

        Returns:
            FieldMapping or None if not found
        """
        data_sources = self.mapping.get('data_sources', {})
        field_config = data_sources.get(field_id)

        if not field_config:
            return None

        return FieldMapping(
            field_id=field_id,
            primary=field_config.get('primary'),
            secondary=field_config.get('secondary'),
            tertiary=field_config.get('tertiary'),
            endpoint=field_config.get('endpoint'),
            field_name=field_config.get('field'),
            statement=field_config.get('statement'),
            calculation=field_config.get('calculation'),
            note=field_config.get('note')
        )

    def fetch_fields(
        self,
        ticker: str,
        fields: Set[str],
        period: str = "annual"
    ) -> FetchResponse:
        """
        Fetch requested fields for a ticker.

        This method:
        1. Plans optimal API call batches
        2. Executes calls through provider clients
        3. Handles fallbacks for missing fields
        4. Returns aggregated response

        Args:
            ticker: Stock ticker symbol
            fields: Set of field IDs to fetch
            period: "annual" or "quarterly"

        Returns:
            FetchResponse with fetched data and metadata
        """
        logger.info(f"Fetching {len(fields)} fields for {ticker}")

        # Clear cache for new ticker
        self._cache.clear()

        response = FetchResponse(
            data={},
            source_metadata={}
        )

        batches = self._plan_batches(fields)

        for provider, field_ids in batches.items():
            self._fetch_provider_batch(
                ticker=ticker,
                provider=provider,
                field_ids=field_ids,
                period=period,
                response=response,
            )

        # Handle missing fields with fallbacks
        still_missing = fields - response.fields_fetched
        if still_missing:
            logger.warning(
                f"{ticker}: {len(still_missing)} fields missing after primary fetch"
            )
            self._fetch_fallbacks(
                ticker=ticker,
                fields=still_missing,
                period=period,
                response=response
            )

        # Final report
        final_missing = fields - response.fields_fetched
        if final_missing:
            response.fields_missing = final_missing
            logger.warning(
                f"{ticker}: {len(final_missing)} fields could not be fetched: "
                f"{sorted(final_missing)}"
            )

        return response

    def _plan_batches(
        self,
        fields: Set[str]
    ) -> Dict[str, Set[str]]:
        """
        Plan optimal API call batches.

        Groups fields by provider to minimize HTTP calls.

        Args:
            fields: Set of field IDs

        Returns:
            Dict[provider] -> set of field IDs
        """
        batches: Dict[str, Set[str]] = {}

        for field_id in fields:
            mapping = self.get_field_mapping(field_id)
            if not mapping:
                logger.warning(f"No mapping found for field: {field_id}")
                continue

            provider = mapping.primary
            batches.setdefault(provider, set()).add(field_id)

        logger.debug(f"Planned {len(batches)} provider batches")
        return batches

    def _fetch_provider_batch(
        self,
        ticker: str,
        provider: str,
        field_ids: Set[str],
        period: str,
        response: FetchResponse
    ):
        """
        Fetch a batch of fields from a single provider endpoint.

        Args:
            ticker: Stock ticker
            provider: Provider name (e.g., 'polygon.io')
            endpoint: API endpoint
            field_ids: List of field IDs to fetch
            period: 'annual' or 'quarterly'
            response: FetchResponse to populate
        """
        logger.debug(
            f"Fetching batch from {provider}: {len(field_ids)} fields"
        )

        client = self.clients.get(provider)
        if not client:
            logger.warning(f"No client configured for provider: {provider}")
            response.warnings.append(
                f"No client for {provider}, skipping {len(field_ids)} fields"
            )
            return

        try:
            cache_key = (provider, tuple(sorted(field_ids)))
            cache_entry = self._cache.get(cache_key)
            if cache_entry:
                data, source_metadata, fetched, warnings = cache_entry
            else:
                data, source_metadata, fetched, warnings = client.fetch_fields(
                    ticker=ticker,
                    fields=field_ids,
                    period=period,
                )
                self._cache[cache_key] = (data, source_metadata, fetched, warnings)

            self._merge_response(response, data, source_metadata, fetched, provider)
            response.warnings.extend(warnings)
        except Exception as exc:  # pragma: no cover - to surface runtime issues
            logger.error(f"Provider {provider} fetch failed: {exc}", exc_info=True)
            response.warnings.append(f"Provider {provider} fetch failed: {exc}")

    def _fetch_fallbacks(
        self,
        ticker: str,
        fields: Set[str],
        period: str,
        response: FetchResponse
    ):
        """
        Attempt to fetch missing fields using fallback providers.

        Args:
            ticker: Stock ticker
            fields: Field IDs that are still missing
            period: 'annual' or 'quarterly'
            response: FetchResponse to populate
        """
        for field_id in fields:
            mapping = self.get_field_mapping(field_id)
            if not mapping:
                continue

            # Try secondary provider
            if mapping.secondary:
                logger.debug(
                    f"Trying secondary provider for {field_id}: "
                    f"{mapping.secondary}"
                )
                self._fetch_provider_batch(
                    ticker=ticker,
                    provider=mapping.secondary,
                    field_ids={field_id},
                    period=period,
                    response=response,
                )

            # Try tertiary provider
            if mapping.tertiary and field_id not in response.fields_fetched:
                logger.debug(
                    f"Trying tertiary provider for {field_id}: "
                    f"{mapping.tertiary}"
                )
                self._fetch_provider_batch(
                    ticker=ticker,
                    provider=mapping.tertiary,
                    field_ids={field_id},
                    period=period,
                    response=response,
                )

    def _merge_response(
        self,
        response: FetchResponse,
        data: Dict[str, Any],
        source_metadata: Dict[str, Any],
        fetched: Set[str],
        provider: str,
    ):
        """Merge provider data into the aggregated FetchResponse."""

        for section, values in data.items():
            if not values:
                continue
            if section not in response.data:
                response.data[section] = {}
            if isinstance(values, dict):
                response.data[section].update(values)
            else:
                response.data[section] = values

        if source_metadata:
            response.source_metadata.update(source_metadata)

        if fetched:
            response.fields_fetched.update(fetched)
            response.providers_used[provider] = response.providers_used.get(provider, 0) + 1


# ===== HELPER FUNCTIONS =====

def validate_mapping(mapping_path: str) -> Tuple[bool, List[str]]:
    """
    Validate data source mapping configuration.

    Args:
        mapping_path: Path to mapping YAML file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    try:
        with open(mapping_path, 'r') as f:
            mapping = yaml.safe_load(f)
    except Exception as e:
        return False, [f"Failed to load mapping: {e}"]

    # Check required sections
    if 'data_sources' not in mapping:
        errors.append("Missing 'data_sources' section")

    if 'api_priority' not in mapping:
        errors.append("Missing 'api_priority' section")

    # Validate data sources
    data_sources = mapping.get('data_sources', {})
    for field_id, config in data_sources.items():
        if 'primary' not in config:
            errors.append(f"Field '{field_id}' missing 'primary' provider")

    return len(errors) == 0, errors
