# Daraz SellerHub - Operations Runbook

This runbook covers critical operational procedures for maintaining SellerHub on DigitalOcean App Platform.

## 1. Rotating FIELD_ENCRYPTION_KEY
If the encryption key is compromised, all sensitive fields (like Daraz API tokens) must be re-encrypted. This is a genuinely hard procedure because tokens must remain valid during rotation.

**Procedure:**
1. Generate a new valid key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
2. Set the old key as `FIELD_ENCRYPTION_FALLBACK_KEYS="old_key_here"` in DigitalOcean env vars.
3. Set the new key as the primary `FIELD_ENCRYPTION_KEY="new_key_here"`.
4. Deploy the application so it can decrypt with the old key but encrypts with the new key.
5. Run the rotation script via console:
   ```bash
   doctl apps exec --component backend -- python manage.py rotate_encryption_keys
   ```
6. Once complete, remove `FIELD_ENCRYPTION_FALLBACK_KEYS` and re-deploy to seal the environment.

## 2. Replaying Failed Sync Windows
If a Celery worker dies during a 120-day sync, the window might become stuck in a `failed` state.
1. Go to the Staff Admin Panel -> Store Health.
2. Locate the failed store and click "Force Resync".
3. This queues a new `SyncJob` which will automatically detect and re-run only the failed chunks within the 120-day span.

## 3. Mass-Expiration of Daraz Tokens
Daraz tokens last 30 days. If the auto-refresh beat task fails silently and tokens mass-expire:
1. Identify affected stores in the Admin Panel (Status: Token Expired).
2. The system automatically sends a critical alert to the seller's configured notification channel (email/in-app).
3. The seller MUST re-authenticate via the Daraz OAuth flow on the frontend. We cannot bypass this.

## 4. Reading Logs
All logs are emitted as structured JSON.
```bash
doctl apps logs <app-id> --type run --component backend
```
For deep tracebacks, check Sentry. Do not rely on App Platform logs for stack traces, as they may be truncated.
