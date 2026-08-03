# Phase 4: Orders, Fulfillment & Profit

## Overview
Phase 4 implements the core Profit Engine logic alongside an interactive, analytics-driven dashboard for Sellers. 

## Profit Formula
The profit for a single OrderItem is computed as follows:

```
net_profit = gross - daraz_fees - seller_shipping - voucher_seller - sku_cost
```

- **Gross**: Computed directly from `OrderItem.paid_price`.
- **Daraz Fees**: Sum of all `FinanceTransaction` amounts linked to this item, excluding the actual "Item Price" (revenue). This includes commission, payment fee, shipping fee, service fees, VAT/WHT.
- **Seller Shipping**: Sum of shipping fees charged to the seller by Daraz.
- **Voucher Seller**: Extracted from `OrderItem.voucher_amount`.
- **SKU Cost**: Evaluated temporally by finding the `SkuCost` row where `effective_from <= order_date`.

### Return & Cancellation Logic
- **Returned / Cancelled / Failed Delivery**: These orders do not contribute positive profit. In cases where forward or reverse shipping costs apply without item refunds from Daraz, the profit may be negative.

### Confidence Levels
Since data ingestion is asynchronous, the engine applies confidence levels to its math:
- `FINAL`: Order is `Delivered`, all finance transactions are ingested, and the `SkuCost` row exists.
- `PROVISIONAL`: Missing or partial finance. The system applies a fallback trailing 30-day average commission rate to approximate profit.
- `INCOMPLETE`: One or more SKUs are missing a historical `SkuCost` row. The profit is flagged and excluded from the headline "Net Profit".

## Unverified Components
The following components have been written but are marked as **Unverified Locally** because they depend on the DigitalOcean remote Postgres database:

1. **Profit Validation**: The fixture-driven `TestProfitEngine.test_profit_math` tests.
2. **Query Performance**: The `select_related` / `prefetch_related` bounds checking for the `/api/orders/` endpoint.
3. **Temporal SkuCost Matching**: Ensuring the engine grabs the *exact* historical cost based on `created_at_daraz`.

## Verification Instructions
Upon deploying to DigitalOcean, run:
```bash
doctl apps exec --component backend -- python manage.py pytest apps.finance apps.orders
```
