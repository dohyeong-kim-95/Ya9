from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .fixtures import MOCK_EVENTS, MOCK_GAME_DETAILS, MOCK_GAMES
from .models import (
    EventsResponse,
    GameDetail,
    HealthResponse,
    TodayGamesResponse,
)

app = FastAPI(title="KBO Live HUD API", version="0.1.0")

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
    return TodayGamesResponse(date=date.today().isoformat(), games=MOCK_GAMES)


@app.get("/api/games/{game_id}", response_model=GameDetail)
def game_detail(game_id: str):
    detail = MOCK_GAME_DETAILS.get(game_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Game not found")
    return detail


@app.get("/api/games/{game_id}/events", response_model=EventsResponse)
def game_events(game_id: str):
    if game_id not in MOCK_GAME_DETAILS:
        raise HTTPException(status_code=404, detail="Game not found")
    events = [e for e in MOCK_EVENTS if e.game_id == game_id]
    return EventsResponse(game_id=game_id, events=events)
