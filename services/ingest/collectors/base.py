"""Abstract base collector interface.

Collectors fetch raw HTML from upstream sources.
Subclass this and implement the fetch methods for each source.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from ..models import RawSnapshot


class BaseCollector(ABC):
    """Abstract upstream data collector."""

    @abstractmethod
    async def fetch_game_list(self, target_date: date) -> RawSnapshot:
        """Fetch the daily schedule/scoreboard page.

        Returns raw HTML snapshot for the given date.
        Raises CollectorError on failure.
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_game_detail(self, game_url: str) -> RawSnapshot:
        """Fetch a single game detail page.

        Args:
            game_url: Full URL or path to the game page.

        Returns raw HTML snapshot.
        Raises CollectorError on failure.
        """
        raise NotImplementedError
