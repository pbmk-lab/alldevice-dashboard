# Codebase Concerns

**Analysis Date:** 2026-03-23

## Tech Debt

**Single-file application design:**
- Issue: UI, configuration, HTTP access, data normalization, KPI computation, chart creation, and page rendering are all coupled in `app.py`
- Files: `app.py`
- Impact: small changes have broad regression risk, review surface is large, and reuse is effectively impossible
- Fix approach: split `app.py` into focused modules for configuration, API access, transformation, analytics, and page rendering

**Inline CSS and markup volume inside Python:**
- Issue: large embedded HTML/CSS blocks are stored directly in `app.py`
- Files: `app.py`
- Impact: styling changes are hard to diff, and visual changes are tightly coupled to business logic edits
- Fix approach: move static CSS and repeated markup helpers out of the main execution path

## Known Bugs

**Task reports and downtime logic share the same file-level execution context:**
- Symptoms: changes for one page can unintentionally affect another because all globals and helpers live together
- Files: `app.py`
- Trigger: edits to common DataFrame names, helper functions, or shared constants
- Workaround: isolate edits carefully and test all four page branches after each change

## Security Considerations

**Secret contract is implicit only:**
- Risk: the app depends on `BASE_URL`, `TASKREPORTS_URL`, `USERNAME`, `PASSWORD`, and `API_KEY` in `st.secrets`, but the repo provides no committed template or validation contract
- Files: `app.py`
- Current mitigation: missing keys fall back to empty strings and the app stops after runtime checks
- Recommendations: add a secret contract template and explicit startup validation with actionable error messages

## Performance Bottlenecks

**All analytics recompute inside one rerun path:**
- Problem: one Streamlit rerun rebuilds multiple grouped DataFrames and Plotly figures from the full dataset
- Files: `app.py`
- Cause: monolithic top-to-bottom execution and figure construction for every page state
- Improvement path: cache normalized source DataFrames separately and lazy-build page-specific figures

## Fragile Areas

**Location-to-line mapping via substring rules:**
- Files: `app.py`
- Why fragile: `LINE_MAPPING` and `extract_line()` rely on free-text keyword inclusion, so upstream naming drift changes classification without any guardrail
- Safe modification: update `LINE_MAPPING` conservatively and validate affected line outputs on real records
- Test coverage: none detected

**Schema assumptions on API response payloads:**
- Files: `app.py`
- Why fragile: downstream code assumes expected keys exist or can be coerced, but there is no schema validation layer between `response.json()` and analytics
- Safe modification: normalize fields immediately after fetch and validate required columns before later computations
- Test coverage: none detected

## Scaling Limits

**Single-process Streamlit scaling:**
- Current capacity: suitable for one small dashboard script and moderate API result sizes
- Limit: complexity and latency both rise as more pages, charts, or API payloads are added to `app.py`
- Scaling path: modularize the app and isolate expensive analytics from render-time concerns

## Dependencies at Risk

**Unpinned Python dependencies:**
- Risk: `requirements.txt` lists bare package names with no versions
- Impact: repeat installs may change behavior or break rendering/data handling
- Migration plan: pin compatible versions in `requirements.txt` and regenerate environments from that locked set

## Missing Critical Features

**Automated tests:**
- Problem: no test suite, smoke test, or fixture-based validation exists for the data pipelines or page logic
- Blocks: safe refactoring of `app.py` and confident upgrades to dependency or API behavior

## Test Coverage Gaps

**Entire dashboard runtime:**
- What's not tested: API response normalization, line classification, anomaly filtering, KPI math, and per-page rendering decisions
- Files: `app.py`
- Risk: regressions will only show up at runtime with live API data
- Priority: High

---

*Concerns audit: 2026-03-23*
