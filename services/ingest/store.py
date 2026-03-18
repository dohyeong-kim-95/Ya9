"""In-memory state store for normalized game data.

Stores latest game summaries, details, and events.
Always returns last known valid state — never returns None for previously-seen games.
"""

from __future__ import annotations

import threading
from datetime import datetime

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.api.app.models import GameDetail, GameEvent, GameSummary  # noqa: E402


class StateStore:
    """Thread-safe in-memory store for the latest normalized game state."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._summaries: dict[str, GameSummary] = {}
        self._details: dict[str, GameDetail] = {}
        self._events: dict[str, list[GameEvent]] = {}
        self._updated_at: dict[str, datetime] = {}
        self._source: dict[str, str] = {}

    def upsert_summary(self, game_id: str, summary: GameSummary, source: str = "mykbo") -> None:
        with self._lock:
            self._summaries[game_id] = summary
            self._updated_at[game_id] = datetime.now()
            self._source[game_id] = source

    def upsert_detail(self, game_id: str, detail: GameDetail, source: str = "mykbo") -> None:
        with self._lock:
            self._details[game_id] = detail
            self._updated_at[game_id] = datetime.now()
            self._source[game_id] = source

    def upsert_events(self, game_id: str, events: list[GameEvent]) -> None:
        with self._lock:
            self._events[game_id] = events

    def get_today_games(self) -> list[GameSummary]:
        with self._lock:
            return list(self._summaries.values())

    def get_game(self, game_id: str) -> GameDetail | None:
        with self._lock:
            return self._details.get(game_id)

    def get_events(self, game_id: str) -> list[GameEvent]:
        with self._lock:
            return self._events.get(game_id, [])

    def get_updated_at(self, game_id: str) -> datetime | None:
        with self._lock:
            return self._updated_at.get(game_id)

    def get_source(self, game_id: str) -> str:
        with self._lock:
            return self._source.get(game_id, "mock")

    def get_global_updated_at(self) -> datetime | None:
        with self._lock:
            if not self._updated_at:
                return None
            return max(self._updated_at.values())

    def has_data(self) -> bool:
        with self._lock:
            return len(self._summaries) > 0

    def clear(self) -> None:
        with self._lock:
            self._summaries.clear()
            self._details.clear()
            self._events.clear()
            self._updated_at.clear()
            self._source.clear()
