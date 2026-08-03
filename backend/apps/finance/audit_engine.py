import datetime
from django.utils import timezone
from decimal import Decimal
from apps.finance.models import FinanceAudit, FinanceIssue, FinanceTransaction
from apps.orders.models import Order, OrderItem
from apps.finance.profit import compute_order_item_profit

def run_audit(audit_id):
    audit = FinanceAudit.objects.get(id=audit_id)
    audit.status = 'running'
    audit.save(update_fields=['status'])
    
    store = audit.store
    
    # Analyze Orders
    orders = Order.objects.filter(
        store=store, 
        created_at_daraz__gte=audit.period_start,
        created_at_daraz__lte=audit.period_end
    ).prefetch_related('items', 'finance_transactions', 'items__finance_transactions')
    
    audit.orders_examined = orders.count()
    
    total_revenue = Decimal(0)
    total_deductions = Decimal(0)
    total_actual = Decimal(0)
    total_expected = Decimal(0)
    loss = Decimal(0)
    
    issues_created = 0
    
    for order in orders:
        for item in order.items.all():
            # compute current known profit
            compute_order_item_profit(item)
            item.refresh_from_db()
            
            # Gross
            gross = item.paid_price
            
            # Deductions
            txs = item.finance_transactions.all()
            deductions = sum(tx.amount for tx in txs if tx.transaction_type != 'Item Price Credit' and tx.amount < 0)
            
            # For simplicity in this mock, we assume 'expected' is simply gross * 0.9 (10% avg fee)
            expected = gross * Decimal('0.9')
            actual = item.profit_amount
            
            total_revenue += gross
            total_deductions += abs(deductions)
            total_actual += actual
            total_expected += expected
            
            diff = actual - expected
            if diff < 0:
                loss += abs(diff)
            
            # Rule 1: MISSING_PAYMENT
            if order.status == 'delivered':
                # Check if > 14 days old and no settlement
                days_old = (timezone.now() - order.created_at_daraz).days
                has_settlement = any(tx.paid_status == 'paid' for tx in txs)
                if days_old > 14 and not has_settlement:
                    FinanceIssue.objects.create(
                        audit=audit, order=order, order_item=item,
                        issue_type='MISSING_PAYMENT', severity='critical',
                        title='Missing Payout',
                        description=f'Order delivered {days_old} days ago but no paid settlement.',
                        amount_impact=gross
                    )
                    issues_created += 1
            
            # Rule 2: NEGATIVE_PROFIT
            if actual < 0 and order.status == 'delivered':
                FinanceIssue.objects.create(
                    audit=audit, order=order, order_item=item,
                    issue_type='NEGATIVE_PROFIT', severity='critical',
                    title='Negative Profit',
                    description=f'Net profit is {actual}.',
                    amount_impact=abs(actual)
                )
                issues_created += 1
                
            # Rule 3: SUSPICIOUS_FEE (Mocked)
            # Example: Shipping fee unusually high
            for tx in txs:
                if 'Shipping' in tx.fee_name and abs(tx.amount) > 500:
                    FinanceIssue.objects.create(
                        audit=audit, order=order, order_item=item,
                        issue_type='SUSPICIOUS_FEE', severity='warning',
                        title='High Shipping Fee',
                        description=f'Shipping fee {tx.amount} is suspicious.',
                        amount_impact=abs(tx.amount),
                        evidence={"tx_id": tx.id}
                    )
                    issues_created += 1
            
            # Rule 5: DOUBLE_DEDUCTION
            fee_counts = {}
            for tx in txs:
                fee_counts[tx.fee_name] = fee_counts.get(tx.fee_name, 0) + 1
                if fee_counts[tx.fee_name] > 1:
                    FinanceIssue.objects.create(
                        audit=audit, order=order, order_item=item,
                        issue_type='DOUBLE_DEDUCTION', severity='critical',
                        title='Double Deduction',
                        description=f'Duplicate fee: {tx.fee_name}',
                        amount_impact=abs(tx.amount),
                        evidence={"tx_id": tx.id}
                    )
                    issues_created += 1
                    
            # Rule 6: REFUND_WITHOUT_RETURN
            has_refund = any(tx.transaction_type == 'Item Price Credit' and tx.amount < 0 for tx in txs)
            if has_refund and order.status != 'returned':
                FinanceIssue.objects.create(
                    audit=audit, order=order, order_item=item,
                    issue_type='REFUND_WITHOUT_RETURN', severity='critical',
                    title='Refund Without Return',
                    description='Item price credited back but no return record found.'
                )
                issues_created += 1
                
            # Rule 7: FEE_ON_CANCELLED
            if order.status == 'canceled' and len(txs) > 0:
                FinanceIssue.objects.create(
                    audit=audit, order=order, order_item=item,
                    issue_type='FEE_ON_CANCELLED', severity='warning',
                    title='Fee on Cancelled Order',
                    description='Daraz charged fees on a cancelled order.'
                )
                issues_created += 1
                
            # Rule 9: COD_MISMATCH
            # Mocked
            pass

    # Rule 8: UNLINKED_TRANSACTION
    unlinked = FinanceTransaction.objects.filter(
        store=store, 
        transaction_date__gte=audit.period_start, 
        transaction_date__lte=audit.period_end,
        order__isnull=True
    )
    for utx in unlinked:
        FinanceIssue.objects.create(
            audit=audit, 
            issue_type='UNLINKED_TRANSACTION', severity='warning',
            title='Unlinked Transaction',
            description=f'Transaction {utx.transaction_number} not linked to any order.',
            amount_impact=abs(utx.amount),
            evidence={"tx_id": utx.id}
        )
        issues_created += 1
        
    audit.revenue_total = total_revenue
    audit.deductions_total = total_deductions
    audit.net_total = total_revenue - total_deductions
    audit.expected_profit = total_expected
    audit.actual_profit = total_actual
    audit.difference = total_actual - total_expected
    audit.loss_amount = loss
    audit.issues_count = issues_created
    
    audit.report = {
        "waterfall": {
            "gross": str(total_revenue),
            "deductions": str(total_deductions),
            "net": str(audit.net_total)
        }
    }
    
    audit.status = 'done'
    audit.save()
