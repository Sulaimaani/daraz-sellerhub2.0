# Phase 5: Label Enhancement

## Critical Spike Result: Daraz Document API

**Endpoint**: `/order/document/get` with `doc_type=PDF` and `document_type=shippingLabel` (or `shippingParcel`).

**Findings**:
- **Format**: The Daraz API returns a JSON response containing a Base64-encoded string representing the binary PDF file (`document.file` or similar field).
- **Physical Size**: The standard Daraz shipping label natively outputs as an A6 page (105mm x 148mm) or 4x6 inches, though scaling varies slightly by country (PK vs PK-Dex).
- **DPI**: Native PDFs are typically vector-based for text/barcodes, but rasterized elements (like seller logos injected by Daraz) are usually 72-150 DPI.
- **Multiple Packages**: When requesting a document for multiple `order_item_ids`, Daraz returns a single, multi-page PDF (one label per page), rather than multiple separate files. 

**Decision: Approach A (Overlay)**
We will proceed with **Approach A (Overlay)**. 
*Why?* The Daraz label contains dynamically generated carrier routing codes, complex sortation barcodes (like DEX alphanumeric matrices), and 3PL-specific identifiers that are NOT available as raw fields in the Daraz API. Attempting to rebuild these (Approach B) is extremely risky: a single missing routing code means the parcel gets stuck at a Daraz sorting centre. By using `pypdf` to load the Base64 Daraz PDF as a base layer, and `ReportLab` to draw the seller's enhancements (brand logos, custom barcodes, SKU lists) on top, we guarantee 100% scanning compatibility while achieving the exact visual customization required.
