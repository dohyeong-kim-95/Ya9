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
- [ ] Lock MVP screens: Home, Game HUD
- [ ] Lock MVP required data fields
- [ ] Lock initial ad placeholder behavior
- [ ] Lock out-of-scope list in repo docs

---

## Phase 1 — Repo and Schema Foundation
### 1.1 Initialize repository
- [ ] Create monorepo or equivalent folder structure
- [ ] Create web app scaffold
- [ ] Create backend API scaffold
- [ ] Create ingestion service scaffold
- [ ] Add shared schema package

### 1.2 Define canonical schema
- [ ] Define `GameSummary`
- [ ] Define `GameDetail`
- [ ] Define `GameEvent`
- [ ] Define enums for status, inning half, event type, importance
- [ ] Add validation layer (Zod or Pydantic depending on boundary)
- [ ] Create mock JSON fixtures

### 1.3 Documentation setup
- [ ] Put PRD, TRD, Tasks.md into `/docs`
- [ ] Add architecture README
- [ ] Add local development README

---

## Phase 2 — Backend API Skeleton
### 2.1 FastAPI setup
- [ ] Create FastAPI app
- [ ] Add `/api/health`
- [ ] Add `/api/games/today`
- [ ] Add `/api/games/{game_id}`
- [ ] Add `/api/games/{game_id}/events`

### 2.2 Mock data serving
- [ ] Serve mock `today` response from fixture
- [ ] Serve mock `game detail` response from fixture
- [ ] Serve mock `events` response from fixture
- [ ] Add response model validation

### 2.3 API quality
- [ ] Add basic error responses
- [ ] Add stale timestamp field to payloads
- [ ] Add CORS config for frontend

---

## Phase 3 — Frontend MVP Screens
### 3.1 Design tokens / layout primitives
- [ ] Define mobile spacing scale
- [ ] Define HUD typography hierarchy
- [ ] Define badge styles for situation tags
- [ ] Define score/count/base panel styling
- [ ] Define ad slot component shell

### 3.2 Home screen
- [ ] Build Today’s Games page
- [ ] Show live games first
- [ ] Show scheduled/final sections
- [ ] Create tappable game cards
- [ ] Render situation tags
- [ ] Add loading/empty/error states

### 3.3 Game HUD screen
- [ ] Build scoreboard header
- [ ] Build inning panel
- [ ] Build count panel
- [ ] Build base occupancy diamond
- [ ] Build batter/pitcher cards
- [ ] Build recent event feed
- [ ] Build persistent game switcher
- [ ] Insert ad placeholder panel

### 3.4 Motion and emphasis
- [ ] Add score-change animation
- [ ] Add new-event entry animation
- [ ] Add base-state highlight animation
- [ ] Add inning transition emphasis

---

## Phase 4 — Ingestion Service
### 4.1 Source adapter framework
- [ ] Define upstream collector interface
- [ ] Define parser interface
- [ ] Define normalization pipeline
- [ ] Define diff engine interface

### 4.2 First source implementation
- [ ] Implement daily game list fetch
- [ ] Implement per-game state fetch
- [ ] Parse raw fields into canonical schema
- [ ] Map raw events into structured event objects
- [ ] Generate derived situation tags

### 4.3 Caching / state storage
- [ ] Store latest game summary by game ID
- [ ] Store latest game detail by game ID
- [ ] Store recent events per game
- [ ] Store last successful update timestamp

### 4.4 Failure handling
- [ ] Handle upstream timeout
- [ ] Handle parse failure per game
- [ ] Preserve last known valid state
- [ ] Add retry/backoff policy

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
