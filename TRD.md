# TRD — KBO Live HUD (Mobile Web MVP)

## 1. Technical Objective
Build a **mobile-web-first KBO live HUD viewer** that ingests public game-state data, normalizes it into a canonical schema, and renders it through a sports-HUD frontend optimized for mobile devices.

The system should be:
- simple enough for a solo operator
- easy to implement via Codex-driven tasks
- robust to partial data loss
- extensible toward monetization and richer visuals

## 2. Proposed Architecture
High-level components:

1. **Ingestion worker**
   - polls upstream data source(s)
   - fetches schedule/game state/event information
   - parses upstream payloads into canonical objects

2. **Normalization layer**
   - converts source-specific fields into internal schema
   - computes derived flags (live, close game, runners in scoring position, etc.)

3. **Cache / state store**
   - stores latest normalized state by game
   - stores recent event history
   - optionally stores short-lived snapshots for diffing

4. **Backend API**
   - serves frontend-ready JSON
   - exposes game list, game detail, recent events

5. **Mobile web frontend**
   - renders home list and game HUD
   - polls backend for updates
   - animates state changes

6. **Ad module layer**
   - placeholder component now
   - replaceable with AdSense later

## 3. Recommended Stack
### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- Framer Motion for lightweight state transitions

### Backend
- Python + FastAPI

### Storage / cache
- Redis preferred for current-state cache and event timelines
- SQLite or Postgres optional for persistent snapshots/logs

### Deployment
- Frontend on Vercel or equivalent
- Backend on a small VPS/container host
- Redis managed or self-hosted depending on budget

## 4. Why polling first
For MVP, **polling is the simplest acceptable model**.

Rationale:
- Upstream likely will not offer stable push delivery for this use case
- Mobile-scale MVP traffic is small
- Polling every few seconds is operationally simple
- Diff-based rendering can still create a live feel

Target approach:
- backend ingestion polls upstream every 2–5 seconds for live games
- frontend polls backend every 2–5 seconds depending on screen/activity

## 5. Canonical Data Model
The frontend must never depend directly on raw upstream fields.

### 5.1 Game summary
```json
{
  "game_id": "20260318_OB_LT_001",
  "status": "live",
  "start_time": "2026-03-18T18:30:00+09:00",
  "away_team": {"code": "OB", "name": "Doosan"},
  "home_team": {"code": "LT", "name": "Lotte"},
  "score": {"away": 3, "home": 2},
  "inning": {"number": 7, "half": "bottom"},
  "count": {"balls": 2, "strikes": 1, "outs": 1},
  "bases": {"first": true, "second": false, "third": true},
  "situation_tags": ["close", "chance", "late"]
}
```

### 5.2 Game detail
```json
{
  "game_id": "20260318_OB_LT_001",
  "status": "live",
  "score": {"away": 3, "home": 2},
  "inning": {"number": 7, "half": "bottom"},
  "count": {"balls": 2, "strikes": 1, "outs": 1},
  "bases": {"first": true, "second": false, "third": true},
  "current_batter": {
    "name": "홍길동",
    "team_code": "LT",
    "order": 4,
    "position": "1B"
  },
  "current_pitcher": {
    "name": "김투수",
    "team_code": "OB",
    "throws": "R"
  },
  "recent_events": []
}
```

### 5.3 Event model
```json
{
  "event_id": "evt_000123",
  "game_id": "20260318_OB_LT_001",
  "sequence": 123,
  "timestamp": "2026-03-18T20:14:04+09:00",
  "event_type": "single",
  "result_label": "안타",
  "zone_label": "좌익수 방면",
  "rbi": 0,
  "score_after": {"away": 3, "home": 2},
  "count_after": {"balls": 0, "strikes": 0, "outs": 1},
  "bases_after": {"first": true, "second": true, "third": false},
  "importance": "medium"
}
```

## 6. Source ingestion principles
1. Fetch upstream source data.
2. Parse into structured game state.
3. Compare with prior state.
4. Generate canonical events from detected state transitions.
5. Store latest state and recent events.
6. Serve frontend-friendly JSON.

### Important rule
Do **not** treat upstream prose as the core domain model.
Use structured facts as the source of truth.

## 7. Derived State / HUD Semantics
The backend should compute derived presentation flags to keep frontend logic simple.

Examples:
- `is_live`
- `is_close_game`
- `is_late_inning`
- `is_scoring_position`
- `is_high_leverage_candidate` (heuristic)
- `is_final`
- `is_extra_innings`

### Situation tag example logic
- `close` → score differential <= 2
- `late` → inning >= 7
- `chance` → runner on second or third while batting team active
- `extra` → inning >= 10

These are heuristic and do not need to be sabermetrically perfect in MVP.

## 8. API Design
### 8.1 GET /api/games/today
Returns all scheduled/live/final games for the day.

Response includes:
- game summaries
- status
- basic situation tags

### 8.2 GET /api/games/{game_id}
Returns full current HUD state for one game.

### 8.3 GET /api/games/{game_id}/events
Returns recent events only.

### 8.4 GET /api/health
Basic health endpoint.

## 9. Frontend Information Architecture
### 9.1 Home screen
Primary mobile page.

Sections:
- header / date
- live games first
- scheduled games
- final games

Each game card shows:
- teams
- score
- inning/status
- situation tags
- micro base/count summary if live

### 9.2 Game HUD screen
Main layout for portrait mobile:
- top: scoreboard strip
- middle: inning + count + bases
- middle/lower: batter and pitcher cards
- bottom: recent events feed
- persistent mini-switcher for other live games
- ad panel near bottom but above critical navigation

### 9.3 Ad slot behavior
The ad component should support three modes:
- placeholder image
- outbound redirect card
- AdSense embed later

The rest of the app must not depend on ad rendering success.

## 10. Update Strategy
### Backend ingestion cadence
- live games: every 2–5 seconds
- scheduled/final games: every 30–60 seconds

### Frontend polling cadence
- home screen: 5–10 seconds if visible
- game detail: 2–5 seconds if visible
- if backgrounded, polling should slow or pause

## 11. Diff and Animation Model
The frontend should not reanimate the whole screen on every poll.
It should:
- compare incoming payload with previous payload
- identify meaningful changes
- trigger scoped animations

Examples:
- score changed → scoreboard pulse
- bases changed → base diamond highlight
- count reset after plate appearance → count transition
- new event appended → event card slide-in
- inning change → inning badge transition

## 12. Error Handling
### Missing data
If some fields are unavailable:
- preserve old valid value briefly if appropriate
- otherwise render placeholder states like `—`
- do not crash the page

### Upstream fetch failure
If ingestion fails temporarily:
- continue serving last known state
- annotate backend logs
- expose stale timestamp to frontend if possible

### Game-specific parse failure
If one game fails to parse:
- isolate failure to that game
- do not fail entire day slate

## 13. Observability / Logging
Minimum logging for MVP:
- ingestion fetch success/failure
- parse success/failure by game
- state diff generation count
- API latency
- frontend fetch failure count if client-side telemetry added later

Optional persistence:
- store raw upstream snapshots for debugging
- retain only short history to control storage

## 14. Security / Legal-aware implementation constraints
- No video/audio rebroadcasting
- No copying broadcaster UI assets
- No dependence on official visual branding beyond normal team naming if legally permissible
- Avoid storing and rendering third-party relay prose as the main product surface

## 15. Directory Structure (Suggested)
```text
repo/
  apps/
    web/
  services/
    api/
    ingest/
  packages/
    schema/
    ui/
  infra/
  docs/
```

More detailed suggestion:
```text
apps/web/
  app/
  components/
  lib/
  hooks/

services/api/
  app/
  routes/
  models/
  services/

services/ingest/
  collectors/
  parsers/
  diff/
  jobs/

packages/schema/
  game.ts
  event.ts

packages/ui/
  scoreboard/
  bases/
  count/
  badges/
  ads/
```

## 16. Implementation Notes for Codex-led Execution
Because implementation will be heavily delegated to Codex, tasks should be:
- small
- file-specific
- acceptance-testable
- schema-first

Best practice:
- lock canonical schema first
- then generate API contracts
- then implement frontend components against mocks
- then wire ingestion

This minimizes thrash from AI-generated code divergence.

## 17. Deferred Technical Features
Not required for MVP:
- websocket push
- user auth
- persistent personalized preferences
- advanced analytics pipeline
- defensive positioning engine
- win probability model
- push notifications
