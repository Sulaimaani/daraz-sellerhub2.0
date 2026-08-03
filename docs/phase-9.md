# Phase 9: Production Readiness & Billing

## Features Built
- **Billing System**: Integrated subscription models, quotas (e.g. stores, API limits), and trial logic into `apps/billing`. Designed to accept manual bank transfers and generic payment gateway adapters.
- **Staff Admin**: A dedicated `/admin-panel` built in React for staff to impersonate users, audit API logs, monitor celery queues, and debug failed syncs.
- **Hardening**: 
  - Integrated Sentry (with PII scrubbing disabled for default fields to protect buyer data).
  - Configured strict Security Headers via `settings/production.py`.
  - Added Deep Healthchecks (`/healthz` covering DB, Redis, Celery) and shallow App Platform routing checks (`/readyz`).
- **Runbooks**: Created `docs/runbook.md` with critical procedures like rotating encryption keys without losing data.
