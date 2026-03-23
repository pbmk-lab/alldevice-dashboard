# Phase 6: Final hardening and workflow cleanup - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 6 is the final hardening pass: reduce avoidable frontend bundle cost, normalize
planning artifacts so GSD can parse the roadmap correctly, and extend smoke coverage to
catch obvious application-level failures.

</domain>

<decisions>
## Implementation Decisions

### Hardening targets
- **D-01:** Prefer incremental hardening over broad refactors; preserve current product behavior.
- **D-02:** Bundle reduction should focus on the chart dependency because it is the dominant cost.
- **D-03:** GSD compatibility matters enough to justify restructuring roadmap and requirements documents.

### the agent's Discretion
- Smoke coverage may remain backend-heavy if it adds meaningful confidence without introducing a frontend test harness.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `frontend/src/shared/ui/chart-panel.tsx`
- `frontend/package.json`
- `tests/backend/`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The chart system is centralized in `frontend/src/shared/ui/chart-panel.tsx`
- Backend smoke verification already exists and can be extended cleanly in `tests/backend/`

### Established Patterns
- Frontend build verification is done through `npm run build`
- Backend smoke verification is done through `.venv\Scripts\python.exe -m pytest tests\backend -q`

### Integration Points
- Plotly bundle choice affects every charted screen at once
- ROADMAP / REQUIREMENTS structure affects future GSD automation and progress reporting

</code_context>

<specifics>
## Specific Ideas

- Replace the full Plotly bundle with a smaller compatible bundle for the currently used chart types.
- Add at least one application-level smoke test beyond the existing route contract tests.

</specifics>

<deferred>
## Deferred Ideas

No new feature work belongs in this phase.

</deferred>

---

*Phase: 06-final-hardening-and-workflow-cleanup*
*Context gathered: 2026-03-23*
