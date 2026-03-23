# Phase 6 Plan 06-01 - Summary

## One-liner

Completed the final hardening pass by making the roadmap GSD-readable, switching charts to a smaller Plotly bundle, and expanding backend smoke coverage.

## What changed

- Rewrote `.planning/ROADMAP.md` into a GSD-compatible structure with phases list, phase details, and progress table
- Reworked `.planning/REQUIREMENTS.md` into ID-based requirements so roadmap and phases can reference stable requirement identifiers
- Switched `frontend/src/shared/ui/chart-panel.tsx` to `plotly.js-basic-dist-min` via the factory wrapper and removed the unused full Plotly bundle dependency
- Extended frontend module declarations in `frontend/src/vite-env.d.ts`
- Added `tests/backend/test_app_smoke.py` for application-level smoke coverage

## Verification

- `node "$env:USERPROFILE\.codex\get-shit-done\bin\gsd-tools.cjs" roadmap analyze` — passed and now detects 6 phases
- `npm run build` in `frontend/` — passed
- `.venv\Scripts\python.exe -m pytest tests\backend -q` — passed (`11 passed`)

## Residual issues

- The basic Plotly bundle is much smaller than the previous full bundle, but the chart chunk is still the heaviest frontend asset.
- No frontend test harness has been added yet; the current hardening coverage remains build-focused on the frontend and test-focused on the backend.
