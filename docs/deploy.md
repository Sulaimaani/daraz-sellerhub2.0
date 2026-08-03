# DigitalOcean App Platform Deployment Guide

This guide walks you through deploying the SellerHub Daraz SaaS to DigitalOcean's App Platform, spinning up the Next.js frontend, Django backend, Celery workers, and attaching Managed Databases.

## 1. Prerequisites
- A DigitalOcean account.
- This code pushed to a GitHub repository that DO can access.
- A registered domain (e.g., `app.yourdomain.com`).

## 2. Infrastructure Setup
1. **Managed Database**: Create a Managed PostgreSQL 16 cluster. Note the connection string (`DATABASE_URL`).
2. **Managed Redis**: Create a Managed Redis 7 cluster. Note the connection string (`REDIS_URL`).
3. **DO Spaces**: Create a Space (S3-compatible bucket) for static files and media. Generate an Access Key and Secret under API settings. Note the endpoint URL (e.g., `nyc3.digitaloceanspaces.com`).

## 3. Daraz OAuth Configuration
1. Note the production domain where this app will live.
2. In the Daraz App Console (for AppKey 505668), register the callback URL:
   `https://<api.yourdomain.com>/api/stores/callback/`
3. Retrieve the Daraz App Key and App Secret.

## 4. App Platform Deployment
1. Go to **Apps** in DigitalOcean and click **Create App**.
2. Alternatively, you can use `doctl` to deploy directly via the `infra/app.yaml` file:
   ```bash
   doctl apps create --spec infra/app.yaml
   ```
3. If using the UI, import the `infra/app.yaml` file. Update the `repo` string in the YAML to match your GitHub repository.

## 5. Environment Variables
You must set the following Secrets/Vars in the DO App Console before the first successful build/run:

| Key | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django Secret Key | `django-insecure-...` |
| `DARAZ_APP_KEY` | App Key 505668 | `505668` |
| `DARAZ_APP_SECRET` | From Daraz Console | `def456...` |
| `DARAZ_REDIRECT_URI` | Full callback URL | `https://api.domain.com/api/stores/callback/` |
| `APP_URL` | Base frontend URL | `https://app.domain.com` |
| `APP_DOMAIN` | Base domain for cookies | `.domain.com` |
| `SPACES_ACCESS_KEY_ID` | Spaces API Key | `DO...` |
| `SPACES_SECRET_ACCESS_KEY` | Spaces Secret | `abc...` |
| `SPACES_BUCKET_NAME` | Bucket name | `daraz-saas-media` |
| `SPACES_ENDPOINT_URL` | Spaces Region URL | `https://nyc3.digitaloceanspaces.com` |
| `SPACES_REGION_NAME` | Region | `nyc3` |
| `DATABASE_URL` | PG Connection | *Provided by DO Managed DB* |
| `REDIS_URL` | Redis Connection | *Provided by DO Managed Redis* |

*(Note: In `app.yaml`, `db.DATABASE_URL` and `redis.REDIS_URL` handle the database links automatically if attached via App Platform, but external clusters require manual entry).*

## 6. Domains
- Assign your custom domains in the DO App settings.
- Route the root domain `app.domain.com` to the `frontend` component.
- Route `api.domain.com` to the `backend` component (or route it via path `/api` on the root domain).

---

## Browser Smoke-Test Checklist

Once the deployment is green, perform these exact steps in your browser to verify the environment.

- [ ] **Frontend Load**: Visit `https://app.domain.com`. Does the login page load without React crashes?
- [ ] **Backend Health**: Visit `https://api.domain.com/healthz/`. Does it return `OK`?
- [ ] **Registration**: Sign up for a new account. Does the DB record get created and log you in?
- [ ] **Cookie Binding**: Check your browser dev-tools (Application > Cookies). Do you see the `refresh_token` cookie set with `HttpOnly`, `Secure`, and `SameSite=Lax`?
- [ ] **Wizard Step 1**: Complete Step 1. Does the DB `OnboardingState` step integer increment to 2?
- [ ] **OAuth Connect**: Click "Connect Daraz Store". Are you correctly bounced to the Daraz login UI with the right redirect URI?
- [ ] **Callback Return**: After Daraz authorization, do you land back on Step 2 with the sync progress showing?
- [ ] **Sync Progress**: Does the sync progress UI update dynamically over ~1-2 minutes until it hits 100%? (This proves Celery, Redis, and Polling are completely healthy).
