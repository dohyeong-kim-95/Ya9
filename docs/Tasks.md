# Tasks — KBO Live HUD (Mobile Web MVP)

## Phase 0 — Product Lock
### 0.1 Confirm product decisions
- [x] Mobile web first
- [x] Sports HUD visual direction
- [x] Small initial audience (~10 users)
- [x] One-tap or near-one-tap game switching as core UX
- [x] Ads reserved for future monetization, not immediate commercialization
- [x] Implementation designed for Codex-led execution

### 0.2 Freeze MVP scope
- [x] Lock MVP screens: Home, Game HUD
- [x] Lock MVP required data fields
- [x] Lock initial ad placeholder behavior
- [x] Lock out-of-scope list in repo docs

---

## Phase 1 — Repo and Schema Foundation ✅
### 1.1 Initialize repository
- [x] Create monorepo or equivalent folder structure
- [x] Create web app scaffold
- [x] Create backend API scaffold
- [x] Create ingestion service scaffold
- [x] Add shared schema package

### 1.2 Define canonical schema
- [x] Define `GameSummary`
- [x] Define `GameDetail`
- [x] Define `GameEvent`
- [x] Define enums for status, inning half, event type, importance
- [x] Add validation layer (Zod or Pydantic depending on boundary)
- [x] Create mock JSON fixtures

### 1.3 Documentation setup
- [x] Put PRD, TRD, Tasks.md into `/docs`
- [ ] Add architecture README
- [ ] Add local development README

---

## Phase 2 — Backend API Skeleton ✅
### 2.1 FastAPI setup
- [x] Create FastAPI app
- [x] Add `/api/health`
- [x] Add `/api/games/today`
- [x] Add `/api/games/{game_id}`
- [x] Add `/api/games/{game_id}/events`

### 2.2 Mock data serving
- [x] Serve mock `today` response from fixture
- [x] Serve mock `game detail` response from fixture
- [x] Serve mock `events` response from fixture
- [x] Add response model validation

### 2.3 API quality
- [x] Add basic error responses
- [ ] Add stale timestamp field to payloads
- [x] Add CORS config for frontend

---

## Phase 3 — Frontend MVP Screens ✅
### 3.1 Design tokens / layout primitives
- [x] Define mobile spacing scale
- [x] Define HUD typography hierarchy
- [x] Define badge styles for situation tags
- [x] Define score/count/base panel styling
- [x] Define ad slot component shell

### 3.2 Home screen
- [x] Build Today’s Games page
- [x] Show live games first
- [x] Show scheduled/final sections
- [x] Create tappable game cards
- [x] Render situation tags
- [x] Add loading/empty/error states

### 3.3 Game HUD screen
- [x] Build scoreboard header
- [x] Build inning panel
- [x] Build count panel
- [x] Build base occupancy diamond
- [x] Build batter/pitcher cards
- [x] Build recent event feed
- [x] Build persistent game switcher
- [x] Insert ad placeholder panel

### 3.4 Motion and emphasis
- [x] Add score-change animation
- [x] Add new-event entry animation
- [x] Add base-state highlight animation
- [x] Add inning transition emphasis

---

## Phase 4A — Source Adapter Skeleton + Live Game Collectors + Parsers

### 4A.1 Source adapter skeleton
Create `services/ingest/` as a standalone Python module with pluggable adapter design.

- [ ] Create `services/ingest/requirements.txt` (httpx, beautifulsoup4, pydantic)
- [ ] Create abstract `BaseCollector` class in `services/ingest/collectors/base.py`
  - Methods: `fetch_game_list(date) -> RawGameListPage`, `fetch_game_detail(game_id) -> RawGamePage`
  - Acceptance: can be subclassed; raises `NotImplementedError` if not overridden
- [ ] Create abstract `BaseParser` class in `services/ingest/parsers/base.py`
  - Methods: `parse_game_list(raw) -> list[GameSummary]`, `parse_game_detail(raw) -> GameDetail`, `parse_play_log(raw) -> list[GameEvent]`
  - Acceptance: can be subclassed
- [ ] Create `NormalizationPipeline` in `services/ingest/pipeline.py`
  - Orchestrates: collector → parser → derived tags → state store
  - Acceptance: takes a collector+parser pair, produces canonical output
- [ ] Create `StateStore` in `services/ingest/store.py`
  - In-memory dict-based store (no Redis yet for MVP)
  - Stores: game summaries, game details, recent events, `last_updated_at` per game
  - Methods: `get_today_games()`, `get_game(game_id)`, `get_events(game_id)`, `upsert_game(...)`, `upsert_events(...)`
  - Acceptance: returns last known valid state; never returns None for previously-seen games

### 4A.2 myKBO Stats collector
Implement `MykboCollector(BaseCollector)` in `services/ingest/collectors/mykbo.py`.

- [ ] Implement `fetch_game_list(date)` — fetch daily schedule/scoreboard page
  - URL pattern: to be confirmed (e.g. `mykbostats.com/scores/YYYY-MM-DD` or similar)
  - Use `httpx.AsyncClient` with browser-like headers (User-Agent, Accept, etc.)
  - Return raw HTML string
  - Acceptance: returns HTML for a valid date; raises `CollectorError` on 403/timeout
- [ ] Implement `fetch_game_detail(game_url)` — fetch single game page
  - URL pattern: to be confirmed (e.g. `mykbostats.com/games/NNNN`)
  - Return raw HTML string
  - Acceptance: returns HTML for a valid game; raises `CollectorError` on failure
- [ ] Store raw HTML snapshots in `RawSnapshot` dataclass with timestamp
  - Purpose: debugging, replay, and parser development
  - Acceptance: raw HTML preserved before any parsing

### 4A.3 Game list parser (`games`)
Implement `MykboParser.parse_game_list()` in `services/ingest/parsers/mykbo.py`.

- [ ] Parse daily schedule page HTML into list of game summaries
  - Extract: game_id (or build from date+teams), away_team, home_team, score, status, start_time, game_url
  - Map status strings to canonical `GameStatus` enum (scheduled/live/final/delay)
  - Acceptance: given saved HTML fixture, produces correct `list[GameSummary]`
- [ ] Handle edge cases:
  - Postponed / cancelled games
  - Double-headers
  - Games not yet started (score = 0-0, status = scheduled)
  - Acceptance: no crash on any edge case; unknown states mapped to `GameStatus.scheduled`

### 4A.4 Linescore parser (`game_team_linescore`)
Implement `MykboParser.parse_linescore()`.

- [ ] Parse game detail page for linescore table
  - Extract: inning-by-inning runs, total R/H/E per team
  - Derive: current inning number, half (top/bottom)
  - Acceptance: given saved HTML fixture, produces correct inning/score state
- [ ] Derive count (B/S/O) and base occupancy if available on page
  - If not available in linescore, mark as "unknown" / zero defaults
  - Acceptance: partial data does not crash; missing fields produce sensible defaults

### 4A.5 Play log parser (`game_play_log`)
Implement `MykboParser.parse_play_log()`.

- [ ] Parse play-by-play section of game detail page
  - Extract per-event: sequence, raw_text, inning, half
  - Preserve raw text verbatim in `raw_text` field before structuring
  - Acceptance: raw text preserved for every event
- [ ] Classify events into canonical `EventType` enum
  - Use keyword matching on Korean text (안타, 삼진, 홈런, 볼넷, etc.)
  - Default to `EventType.other` for unrecognized text
  - Acceptance: common event types correctly classified; unknowns default to `other`
- [ ] Extract structured fields where possible:
  - `result_label` (cleaned display text)
  - `rbi` (if mentioned)
  - `score_after` (if inferable from running linescore)
  - `bases_after` (if inferable; otherwise null)
  - `importance` heuristic (score change = high/critical, strikeout = low, etc.)
  - Acceptance: each event has at least event_type + result_label + raw_text

### 4A.6 Derived situation tags
Implement `compute_situation_tags()` in `services/ingest/pipeline.py`.

- [ ] Compute from current game state:
  - `close` → abs(score diff) <= 2
  - `late` → inning >= 7
  - `chance` → runner on 2nd or 3rd while batting
  - `extra` → inning >= 10
  - `blowout` → abs(score diff) >= 7
  - Acceptance: tags match expected output for mock game states

### 4A.7 Polling scheduler
Implement `IngestionScheduler` in `services/ingest/scheduler.py`.

- [ ] Poll live games every 10–15 seconds
- [ ] Poll scheduled games every 60 seconds
- [ ] Stop polling final games (one last fetch after game ends)
- [ ] Use `asyncio` event loop with configurable intervals
- [ ] Log each fetch cycle: success/failure, game count, duration
- [ ] Acceptance: scheduler runs continuously; respects cadence per game status

---

## Phase 4B — Wire Live Data to API

### 4B.1 Replace mock endpoints with live state store
- [ ] Modify `GET /api/games/today` to read from `StateStore` instead of fixtures
  - Fall back to mock fixtures if store is empty (no scrape yet)
  - Acceptance: returns live data when available, mock when not
- [ ] Modify `GET /api/games/{game_id}` to read from `StateStore`
  - Fall back to mock fixture for the specific game if not in store
  - Acceptance: returns live detail when available
- [ ] Modify `GET /api/games/{game_id}/events` to read from `StateStore`
  - Acceptance: returns live events when available

### 4B.2 Add metadata fields to API responses
- [ ] Add `source` field to all game responses (e.g. `"mykbo"` or `"mock"`)
- [ ] Add `as_of` ISO timestamp (when data was last fetched)
- [ ] Add `stale_seconds` integer (seconds since last successful update)
- [ ] Add `warning` string field (null when fresh; message when stale > threshold)
- [ ] Update Pydantic response models to include these fields
- [ ] Update TypeScript types to include these fields
- [ ] Acceptance: frontend can display staleness indicator

### 4B.3 Startup integration
- [ ] Start ingestion scheduler alongside FastAPI app (shared process or background task)
- [ ] Populate state store on first startup before serving requests
- [ ] Acceptance: API serves live data within 15 seconds of startup

### 4B.4 Failure handling
- [ ] On upstream timeout: log warning, keep last known state, increment stale counter
- [ ] On parse failure for single game: isolate to that game, do not fail entire slate
- [ ] On total fetch failure: serve last known state for all games, set warning
- [ ] Retry policy: 1 retry with 2-second backoff per fetch cycle
- [ ] Acceptance: API never returns 500 due to upstream failure; always returns last known valid state

---

## Phase 4C — Box Score Parsers (Post-Stabilization)
_Only begin after Phase 4A+4B are stable during live games._

### 4C.1 Batting box parser (`game_batting`)
- [ ] Parse batting stats table from game detail page
  - Extract per-batter: name, position, AB, R, H, RBI, BB, SO, AVG
  - Acceptance: given saved HTML fixture, produces correct batting lines

### 4C.2 Pitching box parser (`game_pitching`)
- [ ] Parse pitching stats table from game detail page
  - Extract per-pitcher: name, IP (raw string), H, R, ER, BB, SO, ERA
  - Preserve IP as raw string (do not convert to float)
  - Acceptance: given saved HTML fixture, produces correct pitching lines

### 4C.3 Wire box scores to API
- [ ] Add `GET /api/games/{game_id}/box` endpoint
- [ ] Return batting + pitching for both teams
- [ ] Acceptance: endpoint returns structured box score data

---

## Phase 5 — Wire Real Data to UI
### 5.1 Backend integration
- [ ] Replace mock `/today` with live normalized data
- [ ] Replace mock `/game detail` with live normalized data
- [ ] Replace mock `/events` with live normalized data

### 5.2 Frontend polling
- [ ] Add polling hook for home screen
- [ ] Add polling hook for game detail screen
- [ ] Pause/slow polling when tab hidden
- [ ] Ensure partial payload changes don’t break layout

### 5.3 Diff-aware rendering
- [ ] Track previous payload on client
- [ ] Trigger scoped animations only on meaningful changes
- [ ] Prevent full-screen jitter on each refresh

---

## Phase 6 — Ad-ready Layout
### 6.1 Placeholder implementation
- [ ] Create reusable ad slot component
- [ ] Support static image mode
- [ ] Support outbound link card mode
- [ ] Support “coming soon” fallback mode

### 6.2 Future AdSense readiness
- [ ] Separate ad container from content layout
- [ ] Reserve stable dimensions to reduce layout shift
- [ ] Document insertion points for AdSense later

---

## Phase 7 — QA and Hardening
### 7.1 Functional QA
- [ ] Verify game list renders on mobile widths
- [ ] Verify game detail renders on common mobile widths
- [ ] Verify switching between games is fast and intuitive
- [ ] Verify missing fields degrade gracefully
- [ ] Verify final/scheduled/live states all display correctly

### 7.2 Data QA
- [ ] Compare displayed score/inning/count with source during live games
- [ ] Verify event ordering is stable
- [ ] Verify no duplicate event insertion on refresh
- [ ] Verify stale-state handling works

### 7.3 Performance QA
- [ ] Check mobile Lighthouse basics
- [ ] Check repeated polling does not cause visible jank
- [ ] Check image/icon payloads are small

---

## Phase 8 — Nice-to-Have After MVP
- [ ] Multi-panel view
- [ ] “Most interesting live game” ranking
- [ ] Advanced leverage/chance heuristics
- [ ] Team-specific theming
- [ ] Defensive positioning visualization if viable
- [ ] AI-generated one-line game summaries

---

## Codex Execution Strategy
### Recommended order for prompting Codex
1. Create repo scaffolding
2. Create shared schema and fixtures
3. Build API endpoints with fixtures only
4. Build frontend against fixtures
5. Build ingestion adapter separately
6. Connect ingestion to API
7. Add client polling and animations
8. Add ad placeholder module
9. Run end-to-end QA

### Important guardrails
- [ ] Never let Codex invent multiple incompatible schemas
- [ ] Keep all API contracts fixture-backed before real ingestion
- [ ] Review all parsing logic manually
- [ ] Require each Codex task to have clear acceptance criteria
