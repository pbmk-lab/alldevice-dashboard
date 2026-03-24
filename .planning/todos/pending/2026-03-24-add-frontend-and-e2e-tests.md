---
created: 2026-03-24T08:21:47.979Z
title: Add frontend and e2e tests
area: testing
files:
  - frontend/src/app/router.tsx
  - frontend/src/shared/ui/layout.tsx
  - frontend/src/shared/ui/date-range-picker.tsx
  - frontend/src/features/overview/OverviewPage.tsx
  - frontend/src/features/triage/TriagePage.tsx
---

## Problem

Backend coverage is in place, but the rebuilt React frontend still relies mostly on manual testing plus production builds. The most interactive flows, especially date range selection, filter state propagation, and page rendering across routes, do not yet have automated UI-level protection.

## Solution

Add a frontend test harness and cover the core operator flows. Prioritize route rendering, filter bootstrap, date-range picker behavior, language switching, and at least one end-to-end smoke flow that loads the app and validates a healthy manager dashboard path.
