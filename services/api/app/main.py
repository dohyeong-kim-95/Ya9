"""KBO Live HUD API.

Serves game data from the ingestion state store, falling back to mock
fixtures when no live data is available.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager
from datetime import date, datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add services root to path for ingest imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from .fixtures import MOCK_EVENTS, MOCK_GAME_DETAILS, MOCK_GAMES
from .models import (
    DataMeta,
    EventsResponse,
    GameDetail,
    GameDetailResponse,
    HealthResponse,
    TodayGamesResponse,
)

from services.ingest.store import StateStore  # noqa: E402
from services.ingest.collectors.mykbo import MykboCollector  # noqa: E402
from services.ingest.parsers.mykbo import MykboParser  # noqa: E402
from services.ingest.pipeline import NormalizationPipeline  # noqa: E402
from services.ingest.scheduler import IngestionScheduler  # noqa: E402

logger = logging.getLogger(__name__)

# Global state store — shared between API and scheduler
store = StateStore()
scheduler: IngestionScheduler | None = None


def _build_meta(game_id: str | None = None) -> DataMeta:
    """Build metadata from store state."""
    if not store.has_data():
        return DataMeta(source="mock")

    if game_id:
        updated = store.get_updated_at(game_id)
        source = store.get_source(game_id)
    else:
        updated = store.get_global_updated_at()
        source = "mykbo"

    if not updated:
        return DataMeta(source="mock")

    stale = int((datetime.now() - updated).total_seconds())
    warning = None
    if stale > 60:
        warning = f"Data may be stale ({stale}s since last update)"

    return DataMeta(
        source=source,
        as_of=updated.isoformat(),
        stale_seconds=stale,
        warning=warning,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start ingestion scheduler on startup, stop on shutdown."""
    global scheduler
    try:
        collector = MykboCollector()
        parser = MykboParser()
        pipeline = NormalizationPipeline(collector, parser, store)
        scheduler = IngestionScheduler(pipeline, store)
        await scheduler.start()
        logger.info("Ingestion scheduler started")
    except Exception:
        logger.exception("Failed to start ingestion scheduler — running with mock data only")

    yield

    if scheduler:
        await scheduler.stop()


app = FastAPI(title="KBO Live HUD API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", version="0.1.0")


@app.get("/api/games/today", response_model=TodayGamesResponse)
def games_today():
    # Try live data first, fall back to mock
    if store.has_data():
        games = store.get_today_games()
        meta = _build_meta()
    else:
        games = MOCK_GAMES
        meta = DataMeta(source="mock")

    return TodayGamesResponse(
        date=date.today().isoformat(),
        games=games,
        meta=meta,
    )


@app.get("/api/games/{game_id}", response_model=GameDetailResponse)
def game_detail(game_id: str):
    # Try live data first
    detail = store.get_game(game_id) if store.has_data() else None
    if detail:
        return GameDetailResponse(game=detail, meta=_build_meta(game_id))

    # Fall back to mock
    mock = MOCK_GAME_DETAILS.get(game_id)
    if not mock:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameDetailResponse(game=mock, meta=DataMeta(source="mock"))


@app.get("/api/games/{game_id}/events", response_model=EventsResponse)
def game_events(game_id: str):
    # Try live data first
    if store.has_data():
        events = store.get_events(game_id)
        if events:
            return EventsResponse(game_id=game_id, events=events, meta=_build_meta(game_id))

    # Fall back to mock
    if game_id not in MOCK_GAME_DETAILS:
        raise HTTPException(status_code=404, detail="Game not found")
    events = [e for e in MOCK_EVENTS if e.game_id == game_id]
    return EventsResponse(game_id=game_id, events=events, meta=DataMeta(source="mock"))
