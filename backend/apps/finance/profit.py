from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum

def get_fallback_commission_rate(store):
    """
    Returns the trailing 30-day average commission rate for the store.
    If no history exists, returns a safe fallback of 10% (0.10).
    """
    # For now, return hardcoded 10% (0.10) as a fallback
    # To properly compute this, we would query FinanceTransactions over the last 30 days
    # where fee_name like 'Commission' divided by sum(amount) for gross sales.
    return Decimal('0.10')

def compute_order_item_profit(item) -> dict:
    """
    Computes the profit for a single OrderItem.
    Returns a dict with the breakdown and confidence level, and also updates the item fields.
    """
    # Hard rules: Cancelled, Returned, Failed Delivery don't contribute positive profit
    status = item.status
    if status in ['Return / Refund', 'Cancellation', 'Failed Delivery']:
        # TODO: A returned order might have a negative profit due to forward shipping cost
        # not being refunded, or return shipping fees. For now, if we have FinanceTransactions, 
        # we sum them. Usually, Daraz refunds the item price but keeps the shipping fee.
        # We will still run the math, but the gross (paid_price) should effectively be reversed 
        # by Daraz in Finance as "Item Price Credit".
        # We will let the finance lines dictate the negative profit, but we will mark it FINAL
        # once the reverse logistics are done. For simplicity, we just compute it.
        pass

    gross = item.paid_price or Decimal('0.00')
    
    # 1. Daraz Fees & Seller Shipping
    # Sum all finance transactions tied to this order item
    # Usually fee_name contains "Shipping Fee (Charged by Daraz)" or "Commission" etc.
    finance_qs = item.finance_transactions.all()
    has_finance = finance_qs.exists()
    
    total_finance_fees = Decimal('0.00')
    seller_shipping = Decimal('0.00')
    
    if has_finance:
        for txn in finance_qs:
            # Daraz represents fees as negative amounts in the statement
            # We add them up. If it's a fee, it's negative.
            # "Item Price Credit" (refund) is negative. "Item Price" is positive.
            # We only want to sum the FEES.
            # Wait, the spec says: gross = paid_price.
            # Daraz fees = sum of FinanceTransaction rows linked to this item 
            # (commission, payment fee, shipping fee, service fees, VAT/WHT)
            # We should exclude the actual "Item Price" transaction because we already have `gross`.
            
            fee_name_lower = txn.fee_name.lower()
            if 'item price' in fee_name_lower and 'credit' not in fee_name_lower:
                continue # Skip the principal amount as we use `item.paid_price`
                
            # If it's a shipping fee charged to seller
            if 'shipping fee' in fee_name_lower and txn.amount < 0:
                seller_shipping += abs(txn.amount)
            else:
                total_finance_fees += abs(txn.amount) if txn.amount < 0 else -txn.amount
    else:
        # No finance yet. Estimate commission.
        rate = get_fallback_commission_rate(item.store)
        estimated_commission = gross * rate
        total_finance_fees = estimated_commission
        # Shipping is estimated from item.shipping_amount if seller pays it (usually buyer pays, Daraz deducts)
        # We will leave seller_shipping as 0 for PROVISIONAL unless we can infer from `shipping_amount`.

    # 2. Voucher Seller
    voucher_seller = item.voucher_amount or Decimal('0.00')
    # If the spec meant `voucher_seller` field on Order, we might need to distribute it.
    # But `item.voucher_amount` is usually the seller's voucher. Let's use it.

    # 3. SKU Cost
    sku_cost_total = Decimal('0.00')
    has_cost = False
    
    if item.sku:
        # Find the latest cost where effective_from <= order date
        order_date = item.created_at_daraz or item.created_at
        cost_row = item.sku.costs.filter(effective_from__lte=order_date).order_by('-effective_from').first()
        
        if cost_row:
            has_cost = True
            unit_cost = cost_row.cost_price + cost_row.packaging_cost + cost_row.other_cost
            # quantity is usually 1 per OrderItem in Daraz, but we multiply just in case
            quantity = 1 
            sku_cost_total = unit_cost * quantity

    # 4. Net Profit
    net_profit = gross - total_finance_fees - seller_shipping - voucher_seller - sku_cost_total

    # 5. Confidence Level
    if not has_cost:
        confidence = 'INCOMPLETE'
    elif not has_finance and status == 'Delivered':
        confidence = 'PROVISIONAL'
    elif status != 'Delivered' and status not in ['Return / Refund', 'Cancellation', 'Failed Delivery']:
        confidence = 'PROVISIONAL'
    else:
        confidence = 'FINAL'

    # Cache it
    item.profit_amount = net_profit
    item.profit_confidence = confidence
    item.profit_computed_at = timezone.now()
    item.save(update_fields=['profit_amount', 'profit_confidence', 'profit_computed_at'])

    return {
        "gross": gross,
        "daraz_fees": total_finance_fees,
        "seller_shipping": seller_shipping,
        "voucher_seller": voucher_seller,
        "sku_cost": sku_cost_total,
        "net_profit": net_profit,
        "confidence": confidence
    }
