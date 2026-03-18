"""Polling scheduler for the ingestion service.

Manages periodic fetching with different cadences per game status:
- Live games: every 10-15 seconds
- Scheduled games: every 60 seconds
- Final games: one last fetch, then stop
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime

from .pipeline import NormalizationPipeline
from .store import StateStore

logger = logging.getLogger(__name__)

# Polling intervals (seconds)
LIVE_INTERVAL = 12
SCHEDULED_INTERVAL = 60
GAME_LIST_INTERVAL = 30


class IngestionScheduler:
    """Async scheduler that polls upstream at appropriate cadences."""

    def __init__(self, pipeline: NormalizationPipeline, store: StateStore) -> None:
        self.pipeline = pipeline
        self.store = store
        self._running = False
        self._task: asyncio.Task | None = None
        # Track which final games have been fetched
        self._final_fetched: set[str] = set()

    async def start(self) -> None:
        """Start the scheduler loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Ingestion scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Ingestion scheduler stopped")

    async def _run_loop(self) -> None:
        """Main scheduling loop."""
        last_list_fetch = 0.0
        last_live_fetch = 0.0
        last_scheduled_fetch = 0.0

        while self._running:
            try:
                now = asyncio.get_event_loop().time()

                # Refresh game list periodically
                if now - last_list_fetch >= GAME_LIST_INTERVAL:
                    await self._refresh_game_list()
                    last_list_fetch = now

                # Get current games from store
                games = self.store.get_today_games()

                # Fetch live game details at high frequency
                if now - last_live_fetch >= LIVE_INTERVAL:
                    live_games = [g for g in games if g.status.value == "live"]
                    for game in live_games:
                        url = self.pipeline.game_urls.get(game.game_id, "")
                        if url:
                            await self.pipeline.refresh_game_detail(url, game.game_id)
                    last_live_fetch = now

                # Fetch scheduled game details at low frequency
                if now - last_scheduled_fetch >= SCHEDULED_INTERVAL:
                    scheduled_games = [g for g in games if g.status.value == "scheduled"]
                    for game in scheduled_games:
                        url = self.pipeline.game_urls.get(game.game_id, "")
                        if url:
                            await self.pipeline.refresh_game_detail(url, game.game_id)
                    last_scheduled_fetch = now

                # Fetch final games once
                final_games = [
                    g for g in games
                    if g.status.value == "final" and g.game_id not in self._final_fetched
                ]
                for game in final_games:
                    url = self.pipeline.game_urls.get(game.game_id, "")
                    if url:
                        await self.pipeline.refresh_game_detail(url, game.game_id)
                        self._final_fetched.add(game.game_id)

                # Sleep for 1 second between loop iterations
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Scheduler loop error")
                await asyncio.sleep(5)

    async def _refresh_game_list(self) -> None:
        """Fetch and parse game list. URLs are stored in pipeline.game_urls."""
        today = date.today()
        summaries = await self.pipeline.refresh_game_list(today)

        logger.info(
            "Game list: %d total, %d live, %d scheduled, %d final",
            len(summaries),
            sum(1 for s in summaries if s.status.value == "live"),
            sum(1 for s in summaries if s.status.value == "scheduled"),
            sum(1 for s in summaries if s.status.value == "final"),
        )
