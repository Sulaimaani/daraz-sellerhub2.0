# Phase 7: Return & Claim Manager

## Queue Precedence Order

To enforce the "ONE PHYSICAL PACKAGE APPEARS IN EXACTLY ONE OPERATIONAL QUEUE" rule, the classifier uses the following strict precedence order. 

1. **Needs Data Review** (REVIEW): Evaluated first. If any critical source fields (`returned_at`, `daraz_status_updated_at`, `received_at`) required for deadline math are completely null, the package lands here. The system will never guess.
2. **Review Rejected Claim** (REVIEW): An active claim was rejected by Daraz; waiting for the seller to decide to appeal.
3. **Claim Required** (ACTION REQUIRED): The package has an inspection flagged (damaged, missing, wrong item) AND the 5-business-day window is active (`is_overdue=False`).
4. **Late Claim** (ACTION REQUIRED): Same as above, but the 5-business-day window has expired.
5. **Payout Follow-up** (ACTION REQUIRED): A claim is approved, but the finance audit engine detects the payout is overdue or missing (currently mapped via flags).
6. **Pending Daraz Decision** (WAITING): A claim was filed and is awaiting review from Daraz.
7. **Pending Payout** (WAITING): A claim was approved by Daraz, waiting for the settlement transaction to clear.
8. **Need Checking** (ACTION REQUIRED): The package has been returned to the seller (has a start date), but no `PackageInspection` has been recorded yet.
9. **In Transit To Seller** (WAITING): Daraz marked the package as returning, but the start date hasn't triggered.
10. **Completed** (COMPLETED): Package is inspected, no claim was needed (Received OK), OR the claim lifecycle is fully settled and paid.

## Deadlines & Holiday Maintenance

The 5-business-day window is calculated using `apps/returns/deadlines.py`. 
- It naturally skips Saturdays and Sundays.
- It skips public holidays by querying the `Holiday` table.

> [!WARNING]
> Because Islamic holidays in Pakistan move based on lunar sightings, they cannot be reliably computed. The `Holiday` table **must be populated manually by an admin annually**. If a holiday occurs and is not in the database, sellers will lose 1 day of their official filing window.

## Unverified Components

The following components have been written but are marked as **Unverified Locally** because they depend on the DigitalOcean remote Postgres database:

1. **Business-day Maths**: The recursive loop skipping weekends and `Holiday` models.
2. **Classifier Engine logic**: Ensuring a single queue is returned.
3. **State Machine transitions**: Verifying illegal claim transitions.
4. **Evidence Uploads**: Ensuring EXIF data is stripped and MIME types are enforced when pushing to DigitalOcean Spaces.

## Verification Instructions

Upon deploying to DigitalOcean, run:
```bash
doctl apps exec --component backend -- python manage.py pytest apps.returns.tests
```
