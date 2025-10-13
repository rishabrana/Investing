"""
FetchResponse - Aggregated output from DataSourceRouter fetch operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from storage.json_store import SourceMetadata


@dataclass
class FetchResponse:
    """Response from fetching data."""

    data: Dict[str, Any]
    source_metadata: Dict[str, SourceMetadata]
    fields_fetched: Set[str] = field(default_factory=set)
    fields_missing: Set[str] = field(default_factory=set)
    warnings: List[str] = field(default_factory=list)
    providers_used: Dict[str, int] = field(default_factory=dict)
    raw_payloads: Dict[str, Any] = field(default_factory=dict)


__all__ = ["FetchResponse"]
