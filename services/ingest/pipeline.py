"""Normalization pipeline: collector → parser → derived tags → store."""

from __future__ import annotations

import logging
from datetime import date

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.api.app.models import (  # noqa: E402
    GameDetail,
    GameSummary,
    SituationTag,
)

from .collectors.base import BaseCollector  # noqa: E402
from .models import CollectorError  # noqa: E402
from .parsers.base import BaseParser  # noqa: E402
from .store import StateStore  # noqa: E402

logger = logging.getLogger(__name__)


def compute_situation_tags(
    score_away: int,
    score_home: int,
    inning_number: int,
    inning_half: str,
    bases_second: bool,
    bases_third: bool,
) -> list[SituationTag]:
    """Compute derived situation tags from current game state."""
    tags: list[SituationTag] = []
    diff = abs(score_away - score_home)

    if diff <= 2:
        tags.append(SituationTag.close)
    if diff >= 7:
        tags.append(SituationTag.blowout)
    if inning_number >= 7:
        tags.append(SituationTag.late)
    if inning_number >= 10:
        tags.append(SituationTag.extra)
    if bases_second or bases_third:
        tags.append(SituationTag.chance)

    return tags


class NormalizationPipeline:
    """Orchestrates: collector → parser → derived tags → state store."""

    def __init__(
        self,
        collector: BaseCollector,
        parser: BaseParser,
        store: StateStore,
    ) -> None:
        self.collector = collector
        self.parser = parser
        self.store = store
        # Map game_id → game URL for detail fetching
        self.game_urls: dict[str, str] = {}

    async def refresh_game_list(self, target_date: date) -> list[GameSummary]:
        """Fetch and parse today's game list, updating store and URL map."""
        try:
            snapshot = await self.collector.fetch_game_list(target_date)

            # Use with_urls variant if available (MykboParser)
            if hasattr(self.parser, "parse_game_list_with_urls"):
                results = self.parser.parse_game_list_with_urls(snapshot)
                summaries = []
                for s, url in results:
                    if url:
                        self.game_urls[s.game_id] = url
                    summaries.append(s)
            else:
                summaries = self.parser.parse_game_list(snapshot)

            for s in summaries:
                if s.status.value == "live":
                    s.situation_tags = compute_situation_tags(
                        s.score.away,
                        s.score.home,
                        s.inning.number,
                        s.inning.half.value,
                        s.bases.second,
                        s.bases.third,
                    )
                self.store.upsert_summary(s.game_id, s)

            logger.info("Refreshed game list: %d games, %d URLs", len(summaries), len(self.game_urls))
            return summaries

        except CollectorError as e:
            logger.warning("Failed to fetch game list: %s", e)
            return self.store.get_today_games()
        except Exception:
            logger.exception("Unexpected error refreshing game list")
            return self.store.get_today_games()

    async def refresh_game_detail(self, game_url: str, game_id: str) -> GameDetail | None:
        """Fetch and parse a single game's detail, updating store."""
        try:
            snapshot = await self.collector.fetch_game_detail(game_url)
            detail = self.parser.parse_game_detail(snapshot)
            events = self.parser.parse_play_log(snapshot)

            # Recompute situation tags
            if detail.status.value == "live":
                detail.situation_tags = compute_situation_tags(
                    detail.score.away,
                    detail.score.home,
                    detail.inning.number,
                    detail.inning.half.value,
                    detail.bases.second,
                    detail.bases.third,
                )

            detail.recent_events = events

            self.store.upsert_detail(game_id, detail)
            self.store.upsert_events(game_id, events)

            logger.info("Refreshed game detail: %s (%d events)", game_id, len(events))
            return detail

        except CollectorError as e:
            logger.warning("Failed to fetch game %s: %s", game_id, e)
            return self.store.get_game(game_id)
        except Exception:
            logger.exception("Unexpected error refreshing game %s", game_id)
            return self.store.get_game(game_id)
