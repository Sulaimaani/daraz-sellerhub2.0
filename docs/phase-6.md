# Phase 6: Daraz Finance Audit

## Detection Rules & Thresholds

The Daraz Finance Audit Engine parses every statement and transaction to detect anomalies. The following rules are implemented:

| Issue Type | Severity | Description & Tuning |
|---|---|---|
| `MISSING_PAYMENT` | **Critical** | Flags orders in `Delivered` status for more than **14 days** that do not have any transaction marked as `paid`. Configurable by modifying the `days_old > 14` threshold in `audit_engine.py`. |
| `NEGATIVE_PROFIT` | **Critical** | Flags if the net profit for a specific order item drops below zero after deducting all Daraz fees and costs. |
| `SUSPICIOUS_FEE` | **Warning** | Flags if a fee (e.g., Shipping Fee) is abnormally high. In Phase 6, this is statically mocked (e.g., > 500 PKR), but typically tuned to trigger if the fee exceeds the trailing median by > 25%. |
| `DOUBLE_DEDUCTION` | **Critical** | Flags if the exact same `fee_name` is deducted more than once for a single `OrderItem` during the audit period. |
| `REFUND_WITHOUT_RETURN` | **Critical** | Flags if Daraz applies an `Item Price Credit` deduction, but the order is not marked as `Returned`. |
| `FEE_ON_CANCELLED` | **Warning** | Flags if commission or shipping fees are charged on an order marked strictly as `Canceled`. |
| `UNLINKED_TRANSACTION` | **Warning** | Flags any `FinanceTransaction` record that cannot be linked to a known order. |

## Expected vs Actual Profit Definition
- **Expected Profit**: Defined in the engine as `Gross Revenue - Trailing Average Fees`. In Phase 6, this is mocked as a strict 10% deduction (`gross * 0.90`) to illustrate what the seller *expected* to receive based on average metrics.
- **Actual Profit**: The true `net_profit` computed natively by the Phase 4 Profit Engine, factoring in every single extracted fee line by line.

## Unverified Components
The following components have been written but are marked as **Unverified Locally** because they depend on the DigitalOcean remote Postgres database:

1. **Finance Engine Logic**: The rule detections iterating over thousands of mock transactions via the Celery task.
2. **Decimal Arithmetic**: Ensuring strict precision when computing the `difference` between Expected vs Actual so zero floating point errors occur in the waterfall layout.
3. **Paging and Filtering**: Cross-tenant isolations ensuring User A cannot see User B's audit issues.

## Verification Instructions
Upon deploying to DigitalOcean, run:
```bash
doctl apps exec --component backend -- python manage.py pytest apps.finance.tests_audit
```
