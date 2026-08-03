# Phase 8: Supporting Tools

## Features Built
- **SKU Cost Settings**: Bulk CSV import functionality and inline editing via the `/tools/sku` dashboard. Any changes to a cost invoke a Celery task to recalculate profit for associated order items.
- **Profit Calculator**: A client-side what-if calculator (`/tools/profit`) for estimating Daraz fees, Break-Even points, and Margin % based on current platform rates.
- **Guides**: An MDX-powered documentation system allowing users to search and read guides without leaving the portal.
- **Settings**: A complete account management area to configure Business Profiles, Notification Matrices, and GDPR-compliant account deletion.
