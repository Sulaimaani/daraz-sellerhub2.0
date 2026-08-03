# Daraz Seller SaaS

A multi-tenant SaaS application for Pakistani Daraz sellers.

## Prerequisites

- Docker and Docker Compose
- Node.js (for local frontend dev, though compose handles it)
- Python 3.12 (for local backend dev, though compose handles it)

## Setup

1. Copy `.env.example` to `.env` in the root of the project.
2. Build and start the services:

```bash
make init
# Or manually: make build && make up && make migrate
```

3. Create a superuser:
```bash
make createsuperuser
```

4. The application will be available at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/

## Commands

- `make up`: Start all services in the background.
- `make down`: Stop all services.
- `make build`: Rebuild the docker images.
- `make migrate`: Run database migrations.
- `make makemigrations`: Create new database migrations.
- `make createsuperuser`: Create a superuser account.
- `make shell`: Open the Django shell.
- `make test`: Run pytest tests on the backend.
- `make lint`: Run linters on backend (ruff) and frontend (eslint).
- `make fmt`: Format code for backend (black, ruff) and frontend (prettier).

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `COMPOSE_PROJECT_NAME` | Project namespace for Docker Compose | `darazsaas` |
| `DATABASE_URL` | Postgres connection string | `postgres://daraz_user:daraz_password@postgres:5432/daraz_saas` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `SECRET_KEY` | Django Secret Key | `supersecretkey-for-local-dev` |
| `DEBUG` | Enable Django debug mode | `1` |
| `DJANGO_SETTINGS_MODULE` | Active Django settings | `config.settings.local` |
| `FIELD_ENCRYPTION_KEY` | Fernet key for encrypting DB fields (generate via python cryptography) | (base64 string) |
| `NEXT_PUBLIC_API_URL` | Base URL for frontend API calls | `http://localhost:8000/api` |
| `CORS_ALLOWED_ORIGINS` | Comma separated allowed origins | `http://localhost:3000` |
| `SESSION_COOKIE_DOMAIN` | Domain for Session cookie | `localhost` |
| `REFRESH_COOKIE_DOMAIN` | Domain for Refresh token cookie | `localhost` |
