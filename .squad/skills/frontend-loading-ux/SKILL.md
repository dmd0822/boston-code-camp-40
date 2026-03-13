---
name: "frontend-loading-ux"
description: "Accessible staged loading patterns for the Travel Agent React frontend"
domain: "frontend"
confidence: "high"
source: "manual — Phase 6.2 loading UX polish"
---

## Context

Use this pattern when the frontend knows the backend workflow shape
but does not receive streamed progress events. It fits React views
that need a polished demo-ready loading experience without external
animation libraries.

## Patterns

### Staged Progress Without Backend Streaming

Model the loading journey as a small deterministic phase list in the
frontend. Match visible steps to real backend orchestration so the UI
feels truthful:

1. Phase 1 — sequential destination matching
2. Phase 2 — concurrent POI, event, and weather enrichment
3. Finalizing — itinerary assembly

Keep the active phase in component state and advance it on a timer.
Expose the current phase through:
- a progress bar with `role="progressbar"`
- an `aria-live="polite"` status region
- visible step cards showing complete / active / pending state

### Pair Progress With Skeleton Layouts

Show a skeleton preview of the final itinerary layout beside the
progress indicator. This reassures users that the app is working and
sets expectations for the result structure.

Use CSS shimmer blocks for:
- itinerary header
- destination card title and metadata
- summary lines
- metrics or badge placeholders

### Friendly Errors With Real Retry

Keep the last submitted form payload in the hook layer so the error UI
can offer a true retry action. Present user-friendly recovery copy,
then show the raw technical detail in a secondary treatment.

### Success Reveal Motion

Put entry transitions on the loaded view container instead of wiring
animation logic into the parent. Add `prefers-reduced-motion` fallbacks
for all CSS animations and transitions.

## Examples

Key files in this repo:
- `src/frontend/src/components/LoadingState/LoadingState.tsx`
- `src/frontend/src/components/LoadingState/LoadingState.module.css`
- `src/frontend/src/components/ErrorState/ErrorState.tsx`
- `src/frontend/src/hooks/useItinerary.ts`
- `src/frontend/src/components/ItineraryView/ItineraryView.module.css`

## Anti-Patterns

- Do not use a generic "Loading..." message when the workflow has
  meaningful stages users can understand.
- Do not add heavy animation dependencies for simple loading polish.
- Do not hide failures behind vague copy; include a clear next action.
- Do not animate without honoring `prefers-reduced-motion`.
