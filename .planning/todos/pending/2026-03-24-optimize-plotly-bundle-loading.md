---
created: 2026-03-24T08:21:47.979Z
title: Optimize Plotly bundle loading
area: ui
files:
  - frontend/src/shared/ui/chart-panel.tsx
  - frontend/package.json
  - frontend/vite.config.ts
---

## Problem

The frontend is functional, but Plotly is still the heaviest asset in the build and continues to trigger the large-chunk warning. This increases initial load cost and leaves performance headroom on the table for internal users opening the dashboard over slower network links.

## Solution

Review whether additional chart code splitting, narrower Plotly bundles, or route-level lazy loading can reduce payload size further. Keep the current chart behavior intact while making the heaviest visualization code arrive later or in smaller pieces.
