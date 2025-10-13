"""
FieldMapping - Describes how to retrieve a single data field.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class FieldMapping:
    """Mapping for a single data field."""

    field_id: str
    primary: str
    secondary: Optional[str] = None
    tertiary: Optional[str] = None
    endpoint: Optional[str] = None
    field_name: Optional[str] = None
    statement: Optional[str] = None
    calculation: Optional[str] = None
    note: Optional[str] = None


__all__ = ["FieldMapping"]
