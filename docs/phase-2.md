# Phase 2: Daraz OAuth & Onboarding

## Overview
Phase 2 implements the core OAuth flow with Daraz, stores connection details securely, and provides the onboarding UI.

## Unverified Components
Due to the change in strategy (deploying to DigitalOcean App Platform directly instead of running local Docker/Postgres), the following code components have been **written but remain unverified** locally:
1. `apps/stores/tests.py` - Contains 4 OAuth state test cases, Token crypto checks, Resumability tests, and 429 backoff handling.
2. `apps/onboarding/tests.py` - Contains onboarding step progression checks.
3. Live `SyncJob` integration - While the Celery tasks and Mock Data generation are fully written, they have not run against a real Postgres database yet.

These must be verified in the staging environment on DigitalOcean.

## Local Tunnel Setup (Required for OAuth)
Daraz requires a registered HTTPS callback URI. `localhost` is not supported.

### Using Native PowerShell (Recommended)
1. Run `infra/tunnel.ps1` from your PowerShell terminal.
2. It will output a URL like: `https://<random-words>.trycloudflare.com`
3. Copy this URL.

### Using Docker
Alternatively, run `docker compose --profile tunnel up -d`. The tunnel URL will appear in the `tunnel` service logs.

## Daraz App Configuration
1. Log into your Daraz App Console.
2. Set the Redirect URI to `https://<your-tunnel-url>.trycloudflare.com/api/stores/callback/`.
3. Copy your App Key and App Secret.
4. Update `.env` in the project root:
   ```env
   DARAZ_APP_KEY=your_key
   DARAZ_APP_SECRET=your_secret
   DARAZ_REDIRECT_URI=https://<your-tunnel-url>.trycloudflare.com/api/stores/callback/
   DARAZ_MOCK=true
   ```

## Mock Mode
`DARAZ_MOCK=true` routes all API calls to a local generator (`apps.core.daraz.mock.generator`). This produces fake sellers, 250+ orders, finance transactions, and returns deterministically using Faker.

## Testing
To run the automated tests against the DigitalOcean Staging Postgres database, connect via `DATABASE_URL` and run `pytest`.
