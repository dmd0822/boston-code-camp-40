# Project Context

- **Owner:** Dave Davis
- **Project:** Travel Agent Application — takes customer information, builds personalized itineraries using multiple AI agents
- **Stack:** Python backend (Microsoft Agent Framework), React frontend, Azure Bicep infrastructure
- **Key Agents:** General (destination matching), POI (points of interest), Event (festivals/fairs), Weather (historical forecasts)
- **Grounding:** All agents grounded in web search to reduce hallucination
- **Scope:** MVP — no auth, no persistence of itineraries
- **Created:** 2026-03-12

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### 2026-03-12 — Architecture Design Finalized (Deckard Lead)

**Status:** Approved and ready for implementation sprint

**Key Technical Decisions:**
- **Backend:** FastAPI + Microsoft Agent Framework (customer requirement)
- **Orchestration:** Two-phase deterministic Python (General Agent sequential → POI/Event/Weather concurrent)
- **Grounding:** Mandatory Bing Web Search for all agents (search-first pattern)
- **LLM:** Azure OpenAI (GPT-4o)
- **Frontend:** React + Vite + TypeScript
- **Infrastructure:** Azure Container Apps + Bicep IaC

**Agent Responsibilities:**
- **Pris:** Build React frontend and integrate with backend API

---

### 2026-03-12 — Phase 1 Backend & Tests Complete (Team)

**Status:** Ready for frontend development. Backend API is live with realistic mock data.

**What Pris can do now:**
- **Endpoint ready:** `POST /api/itinerary` returns full mock Lisbon+Porto response with realistic schema
- **Health check:** `GET /api/health` for status monitoring
- **Mock data structure:** All Pydantic models defined; response matches final schema
- **No auth required:** MVP scope — build UI without authentication layer
- **Port:** Backend runs on port 8000 (set CORS `allow_origins` in code if narrowing from `["*"]`)

**API contract reference:**
- Input: `POST /api/itinerary` body with CustomerProfile (interests, budget, travel_dates) and destination list
- Output: Full ItineraryResponse with destinations → itineraries (days) → activities + POIs + events + weather
- Schema file: `src/api/models/itinerary.py` (check for latest fields)

**Frontend structure suggestion:**
- Mirror data structures in TypeScript (manual sync for MVP; auto-gen from OpenAPI is post-MVP)
- Form component for customer input (interests, budget, dates)
- Itinerary display with day-by-day activities, POI cards, events, weather

**Reference Document:** `docs/architecture.md` (37KB, comprehensive MVP architecture)

**What This Means for Pris:**
- POI Agent is a dedicated service within the agent framework
- Fan-out execution in concurrent phase with Event/Weather agents
- Must implement search-grounded reasoning for POI discovery
- Inputs: destination, interests; Output: points of interest list with descriptions
- No authentication or persistence in MVP scope

---

### 2026-03-12 — Phase 4 React Frontend Complete (Pris)

**Status:** ✅ COMPLETE — React 18 + Vite + TypeScript scaffold with 5 core components

**Artifacts Created:**
- `frontend/` directory: 23 files (components, hooks, API client, types, config)
- **5 Production Components:**
  - `CustomerForm` — Form collection (interests, budget, dates, destinations)
  - `ItineraryView` — Main display orchestrating day-by-day layout
  - `DestinationCard` — Individual destination with POI, events, weather cards
  - `LoadingState` — Loading spinner + "Building your itinerary..." UX
  - `ErrorState` — Error display with retry button
- **Custom Hook:** `useItinerary` — State machine (idle → loading → success/error)
- **API Client:** `itineraryApi` — Native fetch, /api proxy, type-safe responses
- **TypeScript Types:** `src/types/itinerary.ts` — Mirrors Pydantic models from backend
- **Styling:** CSS Modules with travel-themed responsive design
- **Build Output:** 204 KB JS (64 KB gzipped)

**Integration:**
- Endpoint: `POST /api/itinerary`
- Base URL configured for `/api` proxy (supports dev and prod)
- Full type safety: CustomerProfile → Itinerary Response flow
- Error handling: Network failures, malformed responses, partial data

**Build Validation:**
- Vite build succeeds with 0 errors
- TypeScript strict mode enabled
- No console warnings

**Key Files:**
- `frontend/src/components/` — All 5 components with individual .tsx files
- `frontend/src/hooks/useItinerary.tsx` — State machine hook
- `frontend/src/api/itineraryApi.ts` — Fetch client with error handling
- `frontend/src/types/itinerary.ts` — TypeScript types (CustomerProfile, ItineraryResponse, etc.)
- `frontend/src/styles/` — CSS Modules (App.module.css, component-specific styles)
- `frontend/vite.config.ts` — Vite configuration
- `frontend/package.json` — Dependencies (React, TypeScript, Vitest, React Testing Library)

**Testing:**
- 66 frontend tests written by Zhora (all passing)
- Component tests: React Testing Library
- Hook tests: useItinerary state transitions
- API client tests: fetch mocking, error scenarios
- Integration tests: end-to-end customer flow

**Notes for Phase 5+:**
- CSS can be enhanced with Tailwind or CSS-in-JS
- OpenAPI code generation for type-safe API client
- Error boundaries recommended for production
- Performance optimization (lazy loading, code splitting)

---

### 2026-03-13 — Phase 6.2 Loading UX Polish (Pris)

**Status:** ✅ COMPLETE — Loading and error states now feel demo-ready without adding heavy animation libraries.

**Architecture / UX Decisions:**
- Frontend mirrors backend orchestration with a deterministic staged progress model: Phase 1 highlights destination matching, Phase 2 highlights POI/event/weather enrichment, and a final state assembles the itinerary.
- Retry now replays the last submitted `CustomerProfile` from `useItinerary`, so the error CTA performs a real retry instead of sending users back through the form first.
- All polish remains lightweight: CSS-only animation, skeleton placeholders, `aria-live` announcements, a semantic progress bar, and `prefers-reduced-motion` fallbacks.

**Patterns to Reuse:**
- Use a single loading component to combine progress messaging, visual animation, and skeleton previews when backend progress is known conceptually but not streamed.
- Keep raw failure details available in the UI, but wrap them in friendlier recovery copy and clear next actions.
- Put reveal transitions on the success view itself (`ItineraryView`) so loaded content always animates in consistently.

**User Preferences / Demo Notes:**
- Dave asked for a polished conference-demo feel with professional, lightweight motion and no external animation libraries.
- Accessible loading and error feedback is a requirement, not optional polish.

**Key Files:**
- `src/frontend/src/components/LoadingState/LoadingState.tsx`
- `src/frontend/src/components/LoadingState/LoadingState.module.css`
- `src/frontend/src/components/ErrorState/ErrorState.tsx`
- `src/frontend/src/components/ErrorState/ErrorState.module.css`
- `src/frontend/src/hooks/useItinerary.ts`
- `src/frontend/src/components/ItineraryView/ItineraryView.tsx`
- `src/frontend/src/components/ItineraryView/ItineraryView.module.css`
- `src/frontend/src/components/__tests__/LoadingState.test.tsx`
- `src/frontend/src/components/__tests__/ErrorState.test.tsx`
- `src/frontend/src/hooks/__tests__/useItinerary.test.ts`
- `src/frontend/src/components/__tests__/CustomerForm.test.tsx`

**Phase 6 Complete:** Backend hardening (Batty), frontend UX polish (Pris), comprehensive error testing (Zhora). 325 tests passing (262 backend + 63 frontend). Conference-demo ready.

---

### 2026-03-28 — Issue #4: Travel Advisory UI (Pris)

**Status:** ✅ COMPLETE — Advisory badges, warning panels, and top-level banner integrated into existing frontend components.

**What Was Built:**
- **TravelAdvisoryBadge** component (new) — dual-mode: compact inline badge (all levels) and expanded warning panel (Level 3-4 only)
  - Level 1 🟢 / Level 2 🟡 — small colored badge in DestinationCard header
  - Level 3 🟠 — expanded warning panel with `role="alert"`, specific warnings list
  - Level 4 🔴 — expanded panel plus "choose alternate destination" recommendation
- **DestinationCard** updated — advisory badge in header, expanded panel below header for severe advisories
- **ItineraryView** updated — top-level `⚠️ Travel Advisory Warnings` banner surfaces Level 3-4 destinations before cards
- **LoadingState** updated — new "Checking travel advisories..." step in Phase 2 (concurrent with POI/events/weather)
- **TypeScript types** — `TravelAdvisory` interface and `AdvisoryLevel` union type added to `itinerary.ts`
- **Graceful degradation** — all components render normally when `travel_advisory` is null/undefined

**Architecture Decisions:**
- Advisory badge uses CSS Modules (consistent with existing component pattern)
- Expanded warning panel uses `role="alert"` for screen reader announcement of severe advisories
- Badge renders as `role="status"` for non-disruptive Level 1-2 indications
- Top-level banner in ItineraryView uses singular/plural grammar for destination count
- `prefers-reduced-motion` respected on all new CSS

**Testing:**
- 24 new tests added (14 TravelAdvisoryBadge + 5 DestinationCard advisory + 5 ItineraryView banner)
- All 91 frontend tests passing
- Test fixtures include Level 1-4 advisories plus destination fixtures with Level 3/4

**Key Files:**
- `src/frontend/src/components/TravelAdvisoryBadge/TravelAdvisoryBadge.tsx`
- `src/frontend/src/components/TravelAdvisoryBadge/TravelAdvisoryBadge.module.css`
- `src/frontend/src/components/__tests__/TravelAdvisoryBadge.test.tsx`
- `src/frontend/src/types/itinerary.ts` (TravelAdvisory, AdvisoryLevel)
- `src/frontend/src/test/fixtures.ts` (level1-4 advisory fixtures)

---

### 2026-03-28 — Travel Advisory Rich Visualization Panel (Pris)

**Status:** ✅ COMPLETE — Dedicated TravelAdvisoryPanel with CSS-only risk gauge, color gradients, and full advisory detail.

**What Was Built:**
- **TravelAdvisoryPanel** component (new) — rich full-detail advisory visualization for all levels:
  - CSS-only four-segment risk gauge (`role="meter"`) with filled/active states
  - Color-gradient backgrounds per level (green → yellow → orange → red)
  - Header with level icon, title, and advisory summary
  - Specific warnings rendered as itemized list with ⚠️ icons
  - Level 4 "Do Not Travel" callout with strong recommendation
  - Source attribution link with "U.S. State Department" branding
  - Semantic `<time>` element for last-updated display
  - `role="alert"` for Level 3-4 (screen reader announcement), `role="region"` for Level 1-2
- **DestinationCard** updated — now renders TravelAdvisoryPanel for all advisory levels (replaces expanded badge which only showed for Level 3-4)
- **29 new tests** covering header rendering, risk gauge ARIA, accessibility roles, warnings, Level 4 callout, source attribution, timestamps, and all-levels smoke tests

**Architecture Decisions:**
- Panel uses CSS Modules with linear gradients (consistent with existing DestinationCard weather styling pattern)
- Risk gauge is pure CSS — no external charting library needed for MVP
- Gauge segments use `opacity` and `transform: scaleY` for visual weight, with `prefers-reduced-motion` fallback
- Advisory panel renders for ALL levels (not just 3-4) — every destination gets the full context
- Kept `TravelAdvisoryBadge` as the inline header badge; `TravelAdvisoryPanel` is the detailed view
- `role="meter"` with full ARIA attributes for the gauge (valuemin/valuemax/valuenow/valuetext)

**Key Files:**
- `src/frontend/src/components/TravelAdvisoryPanel/TravelAdvisoryPanel.tsx`
- `src/frontend/src/components/TravelAdvisoryPanel/TravelAdvisoryPanel.module.css`
- `src/frontend/src/components/__tests__/TravelAdvisoryPanel.test.tsx`
- `src/frontend/src/components/DestinationCard/DestinationCard.tsx` (updated import + usage)

**Test Results:** 120 frontend tests passing (29 new + 91 existing)

