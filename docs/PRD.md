# PRD — KBO Live HUD (Mobile Web MVP)

## 1. Product Overview
KBO Live HUD is a **mobile-web-first live game viewer** that makes users feel like they are “watching” a baseball game even without video. It does this by rendering real-time game-state data as a **sports HUD** rather than a text relay page.

The product is intentionally positioned as a **data-driven companion experience**, not a video substitute, broadcaster clone, or official relay republication service.

## 2. Product Goal
Deliver a lightweight mobile web experience for roughly **10 initial users** that:
- Feels closer to a live viewing experience than standard text commentary
- Supports **fast switching between concurrent KBO games**
- Preserves space and infrastructure for future monetization
- Can be implemented rapidly through AI-assisted development workflows (Codex-led execution)

## 3. Success Criteria
### MVP success looks like:
- Users can open the service on mobile and see all live KBO games for the day
- Users can enter any live game and instantly understand current game state
- Users can switch between games in 1 tap
- Event changes feel “live” through HUD transitions and motion cues
- A reserved ad slot exists in key screens without degrading usability

### Non-MVP business success indicators
- Users voluntarily open the app during live games instead of checking only portal text relay
- Users switch between multiple games during one session
- Placeholder ad/redirect modules can later be swapped for AdSense without redesign

## 4. Target Users
### Primary users
- The creator and a small group of baseball-interested early users (~10 people)
- Users who want **live awareness and immersion** without necessarily watching full video

### Secondary future users
- Fans browsing multiple games in parallel
- Users looking for a lightweight second-screen KBO experience

## 5. Product Positioning
### This product is:
- A **mobile live game-state visualizer**
- A **sports HUD experience**
- A **fast-switch multi-game companion**

### This product is not:
- A video streaming service
- A Tving clone
- An official KBO broadcast replacement
- A verbatim republisher of third-party commentary text

## 6. Core User Problem
Existing text relays provide information, but often do not provide the **feeling of live viewing**.
Users want:
- Immediate understanding of current game tension
- Faster recognition of key situations
- Easy game switching
- A more visual, game-like interface on mobile

## 7. Product Principles
1. **State over prose** — users should understand the game from visual state first.
2. **HUD, not broadcast mimicry** — the interface should feel sports-native without resembling licensed broadcast UI.
3. **Mobile-first clarity** — one-thumb navigation, dense but readable information.
4. **Fast switching matters** — multi-game awareness is a core value proposition.
5. **Structure data, don’t mirror text** — factual event state can be used, but display language should be system-generated.
6. **Ad-safe layout from day one** — reserve monetization surfaces early, even if monetization is delayed.

## 8. MVP Scope
### 8.1 Home screen
A mobile-first “Today’s Games” screen showing all KBO games.

Each game card should display:
- Away team / home team
- Score
- Inning status
- Game status (scheduled / live / final / delay if available)
- Situation badge (examples: `Close`, `Chance`, `Late`, `Extra`)
- Tap target to open detailed HUD

### 8.2 Game HUD screen
The core live-view screen for a single game.

Must include:
- Scoreboard
- Inning and half-inning
- Ball / strike / out count
- Base occupancy
- Current batter / pitcher
- Recent event feed
- One-tap game switch access
- Reserved ad slot / placeholder panel

### 8.3 Game switching
Users should be able to switch between games with minimal friction.

MVP requirement:
- A visible persistent switcher from inside the game screen
- 1 tap or equivalent to navigate to another game

### 8.4 Event updates
When game state changes, the UI should reflect it with lightweight motion and emphasis.

MVP examples:
- Hit
- Strikeout
- Walk
- Score
- Inning transition
- Pitching change

### 8.5 Ad placeholder
A reserved ad area must exist in the interface.

Initial behavior may be:
- Static placeholder image
- Internal banner
- Redirect tile to KBO official page

It must later be replaceable with AdSense-compatible units.

## 9. Desired UX Tone
The visual tone should be **sports HUD**, not gaming sci-fi neon and not TV broadcast copy.

Desired attributes:
- Fast glanceability
- Tension signaling
- Clean competitive sports atmosphere
- Strong hierarchy around score / inning / base state

Avoid:
- Direct imitation of Tving or official broadcast overlays
- Overly futuristic visual clutter
- Heavy dependence on long text commentary blocks

## 10. Functional Requirements
### FR-1. Daily game list
The system shall show the list of today’s KBO games on mobile web.

### FR-2. Live game state
The system shall show near-real-time state for live games, including at minimum:
- score
- inning / half
- ball / strike / out
- base occupancy
- current batter / pitcher if available
- recent structured events

### FR-3. Detailed game page
The system shall provide a per-game HUD view optimized for mobile portrait orientation.

### FR-4. Fast switching
The system shall allow users to switch from one game to another without returning through a deep navigation path.

### FR-5. Event emphasis
The system shall visually emphasize state transitions such as:
- runner in scoring position
- score change
- inning end
- pitching change
- final state

### FR-6. Event feed
The system shall maintain a recent play/event feed built from structured state changes.

### FR-7. Ad slot support
The system shall reserve one or more ad-capable layout regions without requiring a redesign later.

### FR-8. Mobile responsiveness
The system shall prioritize mobile web usability first and may degrade secondary desktop layout gracefully.

### FR-9. Source normalization
The system shall transform upstream source data into an internal canonical schema before rendering.

### FR-10. Source-safe presentation
The system shall avoid presenting upstream text verbatim as the core display format wherever feasible.

## 11. Non-Functional Requirements
### NFR-1. Low-latency feel
The product should feel live. Exact real-time guarantees are not required for MVP, but update cadence should feel timely during active play.

### NFR-2. Mobile performance
The app should load quickly on common mobile devices and remain responsive during state refreshes.

### NFR-3. Reliability
If some data fields are temporarily missing, the app should remain usable and degrade gracefully.

### NFR-4. Small-scale operational simplicity
The MVP should be operable by one person with lightweight infrastructure.

### NFR-5. Extensibility
The system should be easy to expand with:
- richer event animations
- multi-panel view
- advanced stats
- defensive positioning
- monetization modules

## 12. Out of Scope for MVP
- Video or audio streaming
- Official broadcast clip integration
- Full pitch-by-pitch 3D replay
- Personalized accounts
- Notifications
- Chat/social features
- Defensive positioning visualization unless data becomes easy to source
- Complex targeting/analytics ad systems

## 13. Risks and Constraints
### 13.1 Rights / presentation risk
The product must avoid looking like a rebroadcast or a cloned official relay product.

### 13.2 Data source volatility
If the upstream public source changes structure, ingestion may break.

### 13.3 Mobile density challenge
Baseball state is information-dense. The UI must preserve readability on narrow screens.

### 13.4 Solo-build constraint
The implementation will effectively be executed through AI-assisted coding and human review, so docs must stay implementation-friendly and explicit.

## 14. Future Expansion
Potential next steps after MVP:
- Split-screen or quad-view mobile/desktop mode
- “Most interesting game now” ranking
- Win probability / leverage / clutch indicators
- Defensive alignment view if data is available
- AI-generated one-line summaries
- AdSense or direct sponsorship placements

## 15. Open Questions
These do not block MVP start, but should be resolved during implementation:
- Exact upstream source and durability of access
- Precise ad slot dimensions for mobile portrait
- Whether desktop layout gets explicit support in v1 or remains best-effort
