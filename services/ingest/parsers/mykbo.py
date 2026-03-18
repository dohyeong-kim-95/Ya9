"""myKBO Stats HTML parser.

Parses raw HTML from mykbostats.com into canonical schema objects.

IMPORTANT: CSS selectors and HTML structure assumptions are based on
common patterns for sports stats sites. These WILL need adjustment
once actual HTML is inspected. Each parse method has comments marking
the selectors that need verification.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

if TYPE_CHECKING:
    pass

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from services.api.app.models import (  # noqa: E402
    Bases,
    BatterInfo,
    Count,
    EventType,
    GameDetail,
    GameEvent,
    GameStatus,
    GameSummary,
    Importance,
    Inning,
    InningHalf,
    PitcherInfo,
    Score,
    SituationTag,
    TeamInfo,
)

from ..models import RawSnapshot  # noqa: E402
from .base import BaseParser  # noqa: E402

logger = logging.getLogger(__name__)

# ---------- Korean text → EventType mapping ----------
EVENT_KEYWORDS: list[tuple[str, EventType]] = [
    ("홈런", EventType.homerun),
    ("3루타", EventType.triple),
    ("2루타", EventType.double),
    ("안타", EventType.single),
    ("볼넷", EventType.walk),
    ("사구", EventType.hit_by_pitch),
    ("삼진", EventType.strikeout),
    ("병살", EventType.double_play),
    ("희생플라이", EventType.sacrifice_fly),
    ("희생번트", EventType.sacrifice_bunt),
    ("야수선택", EventType.fielders_choice),
    ("실책", EventType.error),
    ("도루", EventType.stolen_base),
    ("도루실패", EventType.caught_stealing),
    ("도루자", EventType.caught_stealing),
    ("폭투", EventType.wild_pitch),
    ("포일", EventType.passed_ball),
    ("보크", EventType.balk),
    ("투수교체", EventType.pitching_change),
    ("교체", EventType.pitching_change),
    ("땅볼", EventType.groundout),
    ("플라이", EventType.flyout),
    ("라인드라이브", EventType.lineout),
    ("아웃", EventType.groundout),
]

# KBO team code mapping (name → code)
TEAM_NAME_TO_CODE: dict[str, str] = {
    "두산": "OB",
    "롯데": "LT",
    "삼성": "SS",
    "한화": "HH",
    "KT": "KT",
    "NC": "NC",
    "LG": "LG",
    "키움": "KW",
    "SSG": "SK",
    "KIA": "HT",
    # Alternate names
    "기아": "HT",
    "넥센": "KW",
    "히어로즈": "KW",
    "SK": "SK",
    "Doosan": "OB",
    "Lotte": "LT",
    "Samsung": "SS",
    "Hanwha": "HH",
    "Kiwoom": "KW",
    "KIA": "HT",
}


def _team_code(name: str) -> str:
    """Convert team name to canonical code."""
    name = name.strip()
    return TEAM_NAME_TO_CODE.get(name, name[:2].upper())


def _classify_event(text: str) -> EventType:
    """Classify Korean play text into canonical EventType."""
    for keyword, event_type in EVENT_KEYWORDS:
        if keyword in text:
            return event_type
    return EventType.other


def _estimate_importance(event_type: EventType, rbi: int) -> Importance:
    """Heuristic importance based on event type and RBI."""
    if rbi >= 2 or event_type == EventType.homerun:
        return Importance.critical
    if rbi == 1:
        return Importance.high
    if event_type in (EventType.single, EventType.double, EventType.triple,
                      EventType.walk, EventType.stolen_base):
        return Importance.medium
    return Importance.low


def _parse_status(text: str) -> GameStatus:
    """Parse game status from Korean status text."""
    text = text.strip().lower()
    if text in ("경기중", "진행중", "live", "진행"):
        return GameStatus.live
    if text in ("종료", "경기종료", "final"):
        return GameStatus.final
    if text in ("예정", "경기전", "scheduled"):
        return GameStatus.scheduled
    if text in ("지연", "우천지연", "delay", "우천"):
        return GameStatus.delay
    if text in ("취소", "cancelled"):
        return GameStatus.cancelled
    return GameStatus.scheduled


class MykboParser(BaseParser):
    """Parser for mykbostats.com HTML pages.

    NOTE: All CSS selectors below are PROVISIONAL and will need tuning
    once we can inspect actual page HTML. The structure is designed so
    that only the selector constants need changing.
    """

    def parse_game_list(self, snapshot: RawSnapshot) -> list[GameSummary]:
        """Parse daily scoreboard page into game summaries.

        Expected HTML structure (NEEDS VERIFICATION):
        - Game cards/rows in a container
        - Each card contains: team names, scores, status, link to detail
        """
        soup = BeautifulSoup(snapshot.html, "html.parser")
        games: list[GameSummary] = []

        # SELECTOR: Adjust these to match actual HTML structure
        # Try common patterns for game cards
        game_elements = (
            soup.select(".game-card")
            or soup.select(".scoreboard-game")
            or soup.select("[class*='game']")
            or soup.select("table.scores tr")
            or soup.select(".schedule-item")
        )

        if not game_elements:
            logger.warning("No game elements found in scoreboard page")
            return games

        for el in game_elements:
            try:
                game = self._parse_game_card(el, snapshot.fetched_at.date())
                if game:
                    games.append(game)
            except Exception:
                logger.exception("Failed to parse game card")
                continue

        return games

    def _parse_game_card(self, el: Tag, game_date: date) -> GameSummary | None:
        """Parse a single game card element into GameSummary."""
        # Extract team names — try multiple selector patterns
        team_els = (
            el.select(".team-name")
            or el.select("[class*='team']")
            or el.select("td.team")
            or el.select("span.team")
        )

        if len(team_els) < 2:
            # Try getting text directly from table cells
            cells = el.select("td")
            if len(cells) >= 4:
                team_els = [cells[0], cells[2]]
            else:
                return None

        away_name = team_els[0].get_text(strip=True)
        home_name = team_els[1].get_text(strip=True)

        # Extract scores
        score_els = (
            el.select(".score")
            or el.select("[class*='score']")
            or el.select("td.score")
        )
        away_score = 0
        home_score = 0
        if len(score_els) >= 2:
            away_score = _safe_int(score_els[0].get_text(strip=True))
            home_score = _safe_int(score_els[1].get_text(strip=True))

        # Extract status
        status_el = (
            el.select_one(".status")
            or el.select_one("[class*='status']")
            or el.select_one(".game-state")
        )
        status = GameStatus.scheduled
        if status_el:
            status = _parse_status(status_el.get_text(strip=True))

        # Extract inning info
        inning_el = (
            el.select_one(".inning")
            or el.select_one("[class*='inning']")
        )
        inning_num = 1
        inning_half = InningHalf.top
        if inning_el:
            inning_text = inning_el.get_text(strip=True)
            inning_num, inning_half = _parse_inning(inning_text)

        # Extract game link for detail page
        link_el = el.select_one("a[href]")
        game_url = ""
        if link_el:
            game_url = link_el.get("href", "")

        # Build game_id
        away_code = _team_code(away_name)
        home_code = _team_code(home_name)
        date_str = game_date.strftime("%Y%m%d")
        game_id = f"{date_str}_{away_code}_{home_code}"

        return GameSummary(
            game_id=game_id,
            status=status,
            start_time=f"{game_date.isoformat()}T18:30:00+09:00",
            away_team=TeamInfo(code=away_code, name=away_name),
            home_team=TeamInfo(code=home_code, name=home_name),
            score=Score(away=away_score, home=home_score),
            inning=Inning(number=inning_num, half=inning_half),
            count=Count(balls=0, strikes=0, outs=0),
            bases=Bases(first=False, second=False, third=False),
            situation_tags=[],
        )

    def parse_game_detail(self, snapshot: RawSnapshot) -> GameDetail:
        """Parse game detail page into full game state.

        Expected HTML structure (NEEDS VERIFICATION):
        - Linescore table
        - Current batter/pitcher info
        - Count and base info (if live)
        """
        soup = BeautifulSoup(snapshot.html, "html.parser")

        # Parse linescore
        linescore = self._parse_linescore(soup)

        # Parse batter/pitcher
        batter = self._parse_current_batter(soup)
        pitcher = self._parse_current_pitcher(soup)

        # Parse count/bases if available
        count = self._parse_count(soup)
        bases = self._parse_bases(soup)

        # Parse status
        status = self._detect_status(soup)

        return GameDetail(
            game_id=linescore.get("game_id", "unknown"),
            status=status,
            start_time=linescore.get("start_time", ""),
            away_team=linescore.get("away_team", TeamInfo(code="??", name="Away")),
            home_team=linescore.get("home_team", TeamInfo(code="??", name="Home")),
            score=linescore.get("score", Score(away=0, home=0)),
            inning=linescore.get("inning", Inning(number=1, half=InningHalf.top)),
            count=count,
            bases=bases,
            situation_tags=[],
            current_batter=batter,
            current_pitcher=pitcher,
            recent_events=[],
        )

    def _parse_linescore(self, soup: BeautifulSoup) -> dict:
        """Parse linescore table from game detail page.

        SELECTOR: These need verification against actual HTML.
        """
        result: dict = {}

        # Find linescore table
        table = (
            soup.select_one("table.linescore")
            or soup.select_one("[class*='linescore']")
            or soup.select_one("table.score-table")
            or soup.select_one("table")
        )

        if not table:
            logger.warning("No linescore table found")
            return result

        rows = table.select("tr")
        if len(rows) < 2:
            return result

        # Assume: row 0 = header or away, row 1 = home (skip header if present)
        data_rows = [r for r in rows if r.select("td")]
        if len(data_rows) < 2:
            return result

        # Away team row
        away_cells = data_rows[0].select("td")
        home_cells = data_rows[1].select("td")

        if away_cells:
            away_name = away_cells[0].get_text(strip=True)
            result["away_team"] = TeamInfo(code=_team_code(away_name), name=away_name)

        if home_cells:
            home_name = home_cells[0].get_text(strip=True)
            result["home_team"] = TeamInfo(code=_team_code(home_name), name=home_name)

        # Scores — typically last few cells are R, H, E
        # Or the total column
        if len(away_cells) >= 2:
            # Try to find R (runs) column — usually second-to-last or marked
            away_runs = _find_runs_total(away_cells)
            home_runs = _find_runs_total(home_cells) if home_cells else 0
            result["score"] = Score(away=away_runs, home=home_runs)

        # Current inning — infer from number of inning columns with data
        inning_count = _count_inning_columns(away_cells, home_cells)
        # Determine half: if home has fewer filled inning cells, it's top of that inning
        away_innings = _count_filled_innings(away_cells)
        home_innings = _count_filled_innings(home_cells)
        if home_innings < away_innings:
            result["inning"] = Inning(number=away_innings, half=InningHalf.top)
        else:
            result["inning"] = Inning(number=home_innings, half=InningHalf.bottom)

        return result

    def _parse_current_batter(self, soup: BeautifulSoup) -> BatterInfo | None:
        """Parse current batter info."""
        el = (
            soup.select_one("[class*='batter']")
            or soup.select_one("[class*='atbat']")
            or soup.select_one(".current-batter")
        )
        if not el:
            return None

        name = el.get_text(strip=True)
        if not name:
            return None

        return BatterInfo(name=name, team_code="", order=0, position="")

    def _parse_current_pitcher(self, soup: BeautifulSoup) -> PitcherInfo | None:
        """Parse current pitcher info."""
        el = (
            soup.select_one("[class*='pitcher']")
            or soup.select_one(".current-pitcher")
        )
        if not el:
            return None

        name = el.get_text(strip=True)
        if not name:
            return None

        return PitcherInfo(name=name, team_code="", throws="R")

    def _parse_count(self, soup: BeautifulSoup) -> Count:
        """Parse ball/strike/out count if displayed on page."""
        # SELECTOR: needs verification
        count_el = (
            soup.select_one("[class*='count']")
            or soup.select_one(".bso")
        )
        if not count_el:
            return Count(balls=0, strikes=0, outs=0)

        text = count_el.get_text(strip=True)
        # Try to parse B-S-O pattern
        m = re.search(r"(\d)\s*[-/]\s*(\d)\s*[-/]\s*(\d)", text)
        if m:
            return Count(
                balls=int(m.group(1)),
                strikes=int(m.group(2)),
                outs=int(m.group(3)),
            )
        return Count(balls=0, strikes=0, outs=0)

    def _parse_bases(self, soup: BeautifulSoup) -> Bases:
        """Parse base occupancy if displayed on page."""
        # SELECTOR: needs verification
        base_el = (
            soup.select_one("[class*='base']")
            or soup.select_one(".diamond")
        )
        if not base_el:
            return Bases(first=False, second=False, third=False)

        # Look for active/occupied base indicators
        first = bool(base_el.select_one("[class*='first'].active, [class*='first'].on, .b1.active"))
        second = bool(base_el.select_one("[class*='second'].active, [class*='second'].on, .b2.active"))
        third = bool(base_el.select_one("[class*='third'].active, [class*='third'].on, .b3.active"))

        return Bases(first=first, second=second, third=third)

    def _detect_status(self, soup: BeautifulSoup) -> GameStatus:
        """Detect game status from page."""
        status_el = (
            soup.select_one("[class*='status']")
            or soup.select_one(".game-state")
        )
        if status_el:
            return _parse_status(status_el.get_text(strip=True))
        return GameStatus.live  # Default for detail pages

    def parse_play_log(self, snapshot: RawSnapshot) -> list[GameEvent]:
        """Parse play-by-play log from game detail page.

        Preserves raw text for each event before structuring.

        SELECTOR: These need verification against actual HTML.
        """
        soup = BeautifulSoup(snapshot.html, "html.parser")
        events: list[GameEvent] = []

        # Find play log container
        log_container = (
            soup.select_one("[class*='play-log']")
            or soup.select_one("[class*='playlog']")
            or soup.select_one("[class*='play-by-play']")
            or soup.select_one(".pbp")
            or soup.select_one("[class*='event']")
        )

        if not log_container:
            logger.warning("No play log container found")
            return events

        # Find individual play entries
        play_entries = (
            log_container.select(".play-entry")
            or log_container.select("[class*='play']")
            or log_container.select("li")
            or log_container.select("tr")
            or log_container.select("div > div")
        )

        for seq, entry in enumerate(play_entries, start=1):
            try:
                event = self._parse_play_entry(entry, seq, snapshot)
                if event:
                    events.append(event)
            except Exception:
                logger.exception("Failed to parse play entry %d", seq)
                continue

        return events

    def _parse_play_entry(self, el: Tag, sequence: int, snapshot: RawSnapshot) -> GameEvent | None:
        """Parse a single play entry into a GameEvent."""
        raw_text = el.get_text(strip=True)
        if not raw_text or len(raw_text) < 2:
            return None

        # Classify event
        event_type = _classify_event(raw_text)

        # Extract RBI if mentioned
        rbi = 0
        rbi_match = re.search(r"(\d)\s*타점", raw_text)
        if rbi_match:
            rbi = int(rbi_match.group(1))
        elif event_type == EventType.homerun:
            rbi = max(1, rbi)

        # Estimate importance
        importance = _estimate_importance(event_type, rbi)

        # Extract inning info from play entry if available
        inning_match = re.search(r"(\d+)회\s*(초|말)", raw_text)
        inning_num = 1
        inning_half = "top"
        if inning_match:
            inning_num = int(inning_match.group(1))
            inning_half = "bottom" if inning_match.group(2) == "말" else "top"

        return GameEvent(
            event_id=f"evt_{sequence:06d}",
            game_id="",  # Will be set by pipeline
            sequence=sequence,
            timestamp=snapshot.fetched_at.isoformat(),
            event_type=event_type,
            result_label=raw_text[:80],  # Truncate for display
            zone_label="",  # Zone info rarely available in text logs
            rbi=rbi,
            score_after=Score(away=0, home=0),  # Needs running total
            count_after=Count(balls=0, strikes=0, outs=0),
            bases_after=Bases(first=False, second=False, third=False),
            importance=importance,
        )


# ---------- Helpers ----------

def _safe_int(text: str) -> int:
    """Parse int from text, returning 0 on failure."""
    try:
        return int(re.sub(r"[^\d-]", "", text) or "0")
    except (ValueError, TypeError):
        return 0


def _parse_inning(text: str) -> tuple[int, InningHalf]:
    """Parse inning text like '7회초' or '5T' into (number, half)."""
    m = re.search(r"(\d+)", text)
    num = int(m.group(1)) if m else 1

    if "말" in text or "B" in text.upper() or "bottom" in text.lower():
        return num, InningHalf.bottom
    return num, InningHalf.top


def _find_runs_total(cells: list[Tag]) -> int:
    """Find the runs total from a linescore row.

    Usually the R column is marked or is one of the last cells.
    """
    # Try finding a cell with class containing 'run' or 'total' or 'R'
    for cell in reversed(cells):
        cls = " ".join(cell.get("class", []))
        if "run" in cls.lower() or "total" in cls.lower() or cls == "R":
            return _safe_int(cell.get_text(strip=True))

    # Fallback: try the second-to-last cell (R, H, E pattern)
    if len(cells) >= 4:
        # Cells: [team, inn1, inn2, ..., R, H, E]
        return _safe_int(cells[-3].get_text(strip=True))

    return 0


def _count_inning_columns(away_cells: list[Tag], home_cells: list[Tag]) -> int:
    """Count inning data columns (excluding team name and R/H/E)."""
    # Typical: [team, 1, 2, 3, ..., R, H, E]
    if len(away_cells) >= 4:
        return len(away_cells) - 4  # team + R + H + E
    return 0


def _count_filled_innings(cells: list[Tag]) -> int:
    """Count how many inning cells have actual score data."""
    if len(cells) < 4:
        return 0
    # Skip first (team name) and last 3 (R, H, E)
    inning_cells = cells[1:-3]
    count = 0
    for c in inning_cells:
        text = c.get_text(strip=True)
        if text and text not in ("-", ""):
            count += 1
    return count
