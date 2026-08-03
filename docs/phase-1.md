# Phase 1 Summary

## What was Built
- **Infrastructure**: Initialized Docker Compose with Postgres, Redis, Backend, Celery Worker, Celery Beat, and Next.js Frontend. Added a `Makefile` for ease of use.
- **Backend Core**: Configured Django 5 with DRF, SimpleJWT, Celery, Redis, Anymail, and drf-spectacular. Added `TimeStampedModel`, tenancy helpers (`TenantQuerySet`, `IsStoreOwner`), crypto utils (Fernet encryption), and Daraz HMAC-SHA256 signature logic with unit tests. Created the `/healthz` endpoint.
- **Accounts**: Built custom `User` (email-based) and `UserProfile` models. Created authentication views with a secure, HTTP-only refresh cookie flow (login, refresh, logout, register, me). Configured throttling (5 requests/hour/IP) on auth routes.
- **Frontend**: Created the Next.js 15 app with Tailwind v4 and shadcn/ui. Added `Dockerfile.dev` and `Dockerfile` (standalone).
- **Testing and Verification**: Configured pytest-django with `UserFactory` in `conftest.py`. Added throttling and cryptography tests.
- **Linters**: Added `ruff`, `black`, `pre-commit` to backend and `eslint`, `prettier` to frontend.

## Defaults Chosen
- Next.js initialized with App Router, TypeScript, ESLint, and Tailwind CSS. Turbopack was disabled as per constraints.
- Used DRF's `ScopedRateThrottle` for auth endpoints.
- Placed environment configuration in `infra/.env.example` and `d:/daraz 3.0/.env`.
- `TimeStampedModel` uses UUID as primary key for better security/scale over sequential IDs.
- Set `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` strictly based on the environment (False in local, True in production).

## TODOs Left Behind
- Frontend authentication hooks, Zustand store implementation, and Axios interceptor for the refresh flow need to be built out on the client side.
- Dashboard shell and marketing pages layout structure are not fully populated with their React components yet (awaiting frontend focused work).
- Need to manually verify Lighthouse scores on the frontend once the marketing pages are fully fleshed out.
- Celery worker needs a dedicated testing script to trigger the debug task from Django shell to verify it fully.
