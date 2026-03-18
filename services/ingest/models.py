"""Internal models for the ingestion service.

Re-exports canonical models from the API layer and adds ingestion-specific types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawSnapshot:
    """Preserves raw upstream HTML with metadata for debugging and replay."""

    url: str
    html: str
    fetched_at: datetime = field(default_factory=datetime.now)
    status_code: int = 200


@dataclass
class CollectorError(Exception):
    """Raised when a collector fails to fetch upstream data."""

    url: str
    status_code: int | None
    message: str

    def __str__(self) -> str:
        return f"CollectorError({self.url}, status={self.status_code}): {self.message}"
