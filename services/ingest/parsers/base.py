"""Abstract base parser interface.

Parsers transform raw HTML into canonical schema objects.
Subclass this and implement the parse methods for each source.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import RawSnapshot

import sys
import os

# Add services directory to path so we can import api models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from services.api.app.models import (  # noqa: E402
    GameDetail,
    GameEvent,
    GameSummary,
)


class BaseParser(ABC):
    """Abstract parser for upstream HTML pages."""

    @abstractmethod
    def parse_game_list(self, snapshot: "RawSnapshot") -> list[GameSummary]:
        """Parse daily schedule page into game summaries."""
        raise NotImplementedError

    @abstractmethod
    def parse_game_detail(self, snapshot: "RawSnapshot") -> GameDetail:
        """Parse game detail page into full game state."""
        raise NotImplementedError

    @abstractmethod
    def parse_play_log(self, snapshot: "RawSnapshot") -> list[GameEvent]:
        """Parse play-by-play section into event list."""
        raise NotImplementedError
