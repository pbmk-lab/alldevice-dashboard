# Phase 1: Foundation and extraction - Discussion Log

> Audit trail only. Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md.

**Date:** 2026-03-23
**Phase:** 1-foundation-and-extraction
**Areas discussed:** platform shape, delivery priorities, local development path

---

## Platform shape

| Option | Description | Selected |
|--------|-------------|----------|
| Split backend/frontend | Separate FastAPI and React apps with shared repo root | ✓ |
| Keep single runtime | Continue with one monolithic Streamlit application | |
| Hybrid temporary shell | Keep Streamlit primary and prototype backend separately | |

**User's choice:** Split backend/frontend while preserving legacy fallback.
**Notes:** Existing rebuild work already moved in this direction, so the discussion resolves around stabilizing that structure instead of reversing it.

---

## Delivery priorities

| Option | Description | Selected |
|--------|-------------|----------|
| Runnable foundation first | Fix startup, verification, and contracts before deeper UX work | ✓ |
| Continue feature expansion | Keep building screens first and defer bootstrap issues | |
| Product polish first | Optimize visuals before runtime confidence | |

**User's choice:** Runnable foundation first.
**Notes:** This aligns with the current repo state: scaffold exists, but runtime confidence is incomplete until backend smoke checks and local dev glue are validated.

---

## Local development path

| Option | Description | Selected |
|--------|-------------|----------|
| Relative `/api` + Vite proxy | Keeps frontend code environment-agnostic and supports local dev cleanly | ✓ |
| Hardcoded backend URL | Faster short-term but brittle across environments | |
| Separate environment-specific fetch layers | More flexible but unnecessary in Phase 1 | |

**User's choice:** Relative `/api` with dev proxy.
**Notes:** This preserves the current frontend API client shape while enabling local development against FastAPI.

---

## the agent's Discretion

- Bundle-size reduction can be handled opportunistically inside foundation hardening.
- Documentation and startup commands can be tightened while preserving the Phase 1 boundary.

## Deferred Ideas

None.
