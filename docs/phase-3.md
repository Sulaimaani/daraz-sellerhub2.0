# Phase 3: The 120-Day Sync Engine & Canonical Data Models

## Overview
Phase 3 establishes the core database schema (`products`, `orders`, `finance`, `returns`) and the robust ETL sync engine that translates Daraz API payloads into a normalized structure.

## Unverified Components
The following components have been fully written but remain **unverified locally** due to the DigitalOcean deployment strategy:
1. **Bulk Upsert Idempotency**: `bulk_create` with `update_conflicts=True` needs verification against the live DO Postgres 16 instance.
2. **Redis Locks**: The `django.core.cache.add` lock strategy relies on the managed Redis instance.
3. **Resumable Sync Windows**: The window-retry logic and mock Daraz payloads need end-to-end execution.

## Mapping Tables & Precedence Rules

### Order Status Precedence
When an order has mixed item statuses, the overall `Order.status` is derived using this priority (1 = highest):
1. Return / Refund
2. Failed Delivery
3. Shipping
4. To Ship
5. Unpaid
6. Delivered
7. Cancellation

### Status Bucket Mapping
| Raw Daraz Status | Our UI Bucket |
|---|---|
| unpaid | Unpaid |
| pending, ready_to_ship | To Ship |
| shipped, in_transit, out_for_delivery | Shipping |
| delivered | Delivered |
| failed, failed_delivery, lost, damaged_by_3pl | Failed Delivery |
| canceled, cancelled | Cancellation |
| returned, return_initiated, refunded, return_shipped_by_buyer, return_rejected | Return / Refund |

## TODOs for Verification against Live API
The following payload fields are mapped safely but require verification against the live Daraz API to confirm exact payload structures once `DARAZ_MOCK=false`:
- **`Customer` PII**: Verify exactly which fields (phone, address1) are provided in `address_shipping`.
- **`Order.is_cod`**: Verify if `payment_method == 'COD'` is universally reliable.
- **`FinanceTransaction.transaction_date`**: Verify exact date string formats.
- **`ReturnPackage.received_at`**: Verify how Daraz represents "returned to seller warehouse" timestamps.

## Data Quality Report
The API endpoint `GET /api/stores/<id>/data-quality/` provides a real-time aggregation of data anomalies:
- Items missing SKUs
- SKUs missing costs
- Returns missing orders
- Unmapped statuses
- Delivered orders missing finance lines

## Testing
Run the pytest suite inside the DigitalOcean App Platform container:
```bash
doctl apps exec --component backend -- python manage.py pytest apps.products apps.orders apps.finance apps.returns apps.core.daraz.mapping
```
