---
created: 2026-03-24T08:21:47.979Z
title: Retire legacy Streamlit fallback
area: general
files:
  - app.py
  - legacy/streamlit_app.py
  - README.md
---

## Problem

The old Streamlit app is still kept as a fallback, which was the right migration choice, but it is now the main remaining legacy path in the repository. Keeping it indefinitely increases maintenance surface and can cause confusion about which app is considered production.

## Solution

After the Coolify deployment is verified and the new FastAPI + React app is stable, remove the fallback from the main operating path. Update documentation so the repository clearly points to the new runtime as the single supported application.
