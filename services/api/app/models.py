from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class GameStatus(str, Enum):
    scheduled = "scheduled"
    live = "live"
    final = "final"
    delay = "delay"
    cancelled = "cancelled"


class InningHalf(str, Enum):
    top = "top"
    bottom = "bottom"


class EventType(str, Enum):
    single = "single"
    double = "double"
    triple = "triple"
    homerun = "homerun"
    walk = "walk"
    hit_by_pitch = "hit_by_pitch"
    strikeout = "strikeout"
    groundout = "groundout"
    flyout = "flyout"
    lineout = "lineout"
    double_play = "double_play"
    fielders_choice = "fielders_choice"
    sacrifice_fly = "sacrifice_fly"
    sacrifice_bunt = "sacrifice_bunt"
    error = "error"
    stolen_base = "stolen_base"
    caught_stealing = "caught_stealing"
    wild_pitch = "wild_pitch"
    passed_ball = "passed_ball"
    balk = "balk"
    pitching_change = "pitching_change"
    inning_change = "inning_change"
    other = "other"


class Importance(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class SituationTag(str, Enum):
    close = "close"
    late = "late"
    chance = "chance"
    extra = "extra"
    blowout = "blowout"


class TeamInfo(BaseModel):
    code: str
    name: str


class Score(BaseModel):
    away: int
    home: int


class Inning(BaseModel):
    number: int
    half: InningHalf


class Count(BaseModel):
    balls: int
    strikes: int
    outs: int


class Bases(BaseModel):
    first: bool
    second: bool
    third: bool


class BatterInfo(BaseModel):
    name: str
    team_code: str
    order: int
    position: str


class PitcherInfo(BaseModel):
    name: str
    team_code: str
    throws: str


class GameEvent(BaseModel):
    event_id: str
    game_id: str
    sequence: int
    timestamp: str
    event_type: EventType
    result_label: str
    zone_label: str
    rbi: int
    score_after: Score
    count_after: Count
    bases_after: Bases
    importance: Importance


class GameSummary(BaseModel):
    game_id: str
    status: GameStatus
    start_time: str
    away_team: TeamInfo
    home_team: TeamInfo
    score: Score
    inning: Inning
    count: Count
    bases: Bases
    situation_tags: list[SituationTag]


class GameDetail(BaseModel):
    game_id: str
    status: GameStatus
    start_time: str
    away_team: TeamInfo
    home_team: TeamInfo
    score: Score
    inning: Inning
    count: Count
    bases: Bases
    situation_tags: list[SituationTag]
    current_batter: Optional[BatterInfo]
    current_pitcher: Optional[PitcherInfo]
    recent_events: list[GameEvent]


class DataMeta(BaseModel):
    """Metadata about the data freshness and source."""

    source: str = "mock"
    as_of: Optional[str] = None
    stale_seconds: int = 0
    warning: Optional[str] = None


class TodayGamesResponse(BaseModel):
    date: str
    games: list[GameSummary]
    meta: DataMeta = DataMeta()


class GameDetailResponse(BaseModel):
    """Wrapper around GameDetail with metadata."""

    game: GameDetail
    meta: DataMeta = DataMeta()


class EventsResponse(BaseModel):
    game_id: str
    events: list[GameEvent]
    meta: DataMeta = DataMeta()


class HealthResponse(BaseModel):
    status: str
    version: str
