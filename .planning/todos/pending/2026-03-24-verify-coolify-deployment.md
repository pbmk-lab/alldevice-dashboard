---
created: 2026-03-24T08:21:47.979Z
title: Verify Coolify deployment
area: general
files:
  - README.md
  - Dockerfile
  - docker-compose.yml
  - backend/app/core/config.py
---

## Problem

The application is ready for deployment, but the actual Coolify rollout has not been executed yet. We still need a real production-style verification pass to confirm that environment variables, health checks, reverse proxying, and upstream connectivity all behave correctly outside the local development environment.

## Solution

Deploy the current Docker-based app in Coolify using the simplified `ALLDEVICE_API_BASE_URL` configuration. Verify `/health`, `/api/filters`, overview loading, and work reports loading with real environment variables. Capture any Coolify-specific runtime quirks and feed them back into the docs or config if needed.
