# Codebase Structure

**Analysis Date:** 2026-03-23

## Directory Layout

```text
alldevice-dashboard/
├── .planning/        # GSD planning and codebase-map artifacts
├── app.py            # Single application entrypoint and all runtime logic
└── requirements.txt  # Python dependency manifest
```

## Directory Purposes

**`.planning/`:**
- Purpose: GSD workflow state and analysis artifacts
- Contains: codebase mapping documents under `.planning/codebase/`
- Key files: `.planning/codebase/STACK.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/CONCERNS.md`

## Key File Locations

**Entry Points:**
- `app.py`: Streamlit entrypoint, API client, analytics engine, and UI renderer

**Configuration:**
- `requirements.txt`: runtime dependencies
- External Streamlit secret store consumed by `app.py`: not committed in this repo

**Core Logic:**
- `app.py`: all domain logic currently lives here

**Testing:**
- Not detected

## Naming Conventions

**Files:**
- Flat root-level naming with generic app bootstrap names: `app.py`, `requirements.txt`

**Directories:**
- Only workflow metadata directory exists in repo: `.planning/`

## Where to Add New Code

**New Feature:**
- Current repository structure forces feature code into `app.py`
- Safe placement within current layout:
  - shared constants/helpers near the top of `app.py`
  - fetch/transformation logic in the middle of `app.py`
  - page rendering branches near the bottom of `app.py`

**New Component/Module:**
- No module directories exist yet
- First structural refactor should introduce dedicated packages rather than keep extending `app.py`

**Utilities:**
- Current shared helper pattern is function-level reuse inside `app.py`, e.g. `apply_common_layout()` and `extract_line()`

## Special Directories

**`.planning/`:**
- Purpose: GSD process artifacts
- Generated: Yes
- Committed: currently present in working tree

**`.git/`:**
- Purpose: repository metadata
- Generated: Yes
- Committed: No

---

*Structure analysis: 2026-03-23*
