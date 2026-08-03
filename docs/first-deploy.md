# Daraz SellerHub - First Deploy Runbook

Follow these exact steps from top to bottom to deploy Daraz SellerHub safely to DigitalOcean App Platform for the very first time.

## Phase 1: Infrastructure Provisioning

1. **Create Managed Database (PostgreSQL)**
   - Go to DO Databases -> Create Database Cluster.
   - **Engine**: PostgreSQL 16
   - **Size**: Basic, $15/mo node (1GB RAM, 10GB Disk is sufficient for initial launch).
   - **Region**: NYC3
   - Save the Connection String (Public network for now if App Platform requires it, or VPC if configured).

2. **Create Managed Redis**
   - Go to DO Databases -> Create Database Cluster.
   - **Engine**: Redis 7
   - **Size**: Basic, $15/mo node.
   - **Region**: NYC3
   - Save the Connection String (starts with `rediss://`).

3. **Create Object Storage (Spaces)**
   - Go to DO Spaces -> Create Space.
   - **Region**: NYC3
   - **Name**: `daraz-saas-assets` (must be globally unique, adjust if needed).
   - **CDN**: Enable CDN (optional but recommended for static files).
   - Go to API -> Generate New Key. Save the **Access Key** and **Secret Key**.

## Phase 2: Generating Application Secrets

Run the following locally in your terminal to generate safe keys:

1. **SECRET_KEY** (Django core cryptography):
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

2. **FIELD_ENCRYPTION_KEY** (For Daraz tokens):
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

Keep both of these values safe. If `FIELD_ENCRYPTION_KEY` is lost, all connected stores will instantly disconnect and require re-authentication.

## Phase 3: DigitalOcean App Platform Setup

1. **Create App**
   - Go to DO App Platform -> Create App.
   - Connect your GitHub repository.
   - DO NOT deploy immediately. We need to configure the `app.yaml`.

2. **Upload `infra/app.yaml`**
   - In the App Settings, find "App Spec".
   - Replace the entire default JSON/YAML with the contents of your `infra/app.yaml`.
   - Before saving, ensure `your-github-user/daraz-saas` is replaced with your actual GitHub repository slug.

3. **Set App-Level Environment Variables (Bulk Editor)**
   - Once the spec is saved, navigate to the **Environment** tab and edit bulk variables. Paste the following, replacing the `<values>`:

```text
SECRET_KEY=<your_generated_secret_key>
FIELD_ENCRYPTION_KEY=<your_generated_encryption_key>
DARAZ_APP_KEY=<your_daraz_app_key>
DARAZ_APP_SECRET=<your_daraz_app_secret>
DARAZ_REDIRECT_URI=https://<your_domain>/api/auth/daraz/callback
SPACES_ACCESS_KEY_ID=<your_spaces_access_key>
SPACES_SECRET_ACCESS_KEY=<your_spaces_secret_key>
SPACES_BUCKET_NAME=<your_spaces_name>
SPACES_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
SPACES_REGION_NAME=nyc3
DARAZ_MOCK=true
```

*(Note: `DATABASE_URL` and `REDIS_URL` are automatically bound by App Platform if you link the databases during creation, otherwise, set them here too).*

4. **Deploy**
   - Click "Deploy Now". The build will take approximately 3-5 minutes.
   - The `release` job will automatically run `python manage.py migrate` and `collectstatic`.

## Phase 4: Verification & Empty State

1. **Health Probes**
   - Verify that App Platform is reporting the components as "Healthy". It uses `/healthz/` which checks Postgres, Redis, and Celery worker heartbeats.

2. **Create Superuser**
   - Open the "Console" tab for the `backend` component in DO.
   - Run: `python manage.py createsuperuser`
   - Enter your email (`admin@example.com`) and a strong password.

3. **Verify Empty State (Mock Mode)**
   - Open the Live App URL.
   - Log in using your new credentials.
   - Because `DARAZ_MOCK=true` is set, you can safely walk through the onboarding wizard.
   - Connect a "Mock Store". The system will use faker data to populate orders, products, and finance transactions.
   - Click through the Profit Calculator, Claims Manager, and Dashboard to ensure no 500 errors occur. The app expects an empty state initially and will render "No Data" states gracefully.

4. **Go Live**
   - Once verified, go back to the App Platform Environment tab.
   - Change `DARAZ_MOCK=true` to `DARAZ_MOCK=false`.
   - This triggers a re-deploy. Upon completion, real Daraz API calls will be made.
