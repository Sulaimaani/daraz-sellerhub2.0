from .deadlines import calculate_deadline

def classify_package(package):
    """
    Given a ReturnPackage, returns the exact queue it belongs to based on strict precedence.
    One physical package appears in exactly one operational queue.
    """
    dl_info = calculate_deadline(package)
    
    # 1. Needs Data Review
    if dl_info['error'] == 'needs_data_review':
        return 'Needs Data Review'
        
    claims = package.claims.all()
    active_claim = claims.first() # Assume we order by recent or active
    
    has_inspections = package.inspections.exists()
    requires_claim = False
    
    if has_inspections:
        latest_inspection = package.inspections.order_by('-recorded_at').first()
        if latest_inspection.condition in ['damaged', 'wrong_item', 'missing', 'accessories_missing', 'package_not_received']:
            requires_claim = True
            
    # 2. Review Rejected Claim
    if active_claim and active_claim.status == 'rejected':
        return 'Review Rejected Claim'
        
    # 3. Claim Required & 4. Late Claim
    if requires_claim and not active_claim:
        if not dl_info['is_overdue']:
            return 'Claim Required'
        else:
            return 'Late Claim'
            
    # 5. Payout Follow-up
    # Example logic: if claim is approved but finance audit found missing payout
    if active_claim and active_claim.status in ['approved', 'partially_approved']:
        # If it's been approved for X days and no finance transaction...
        # Mocking logic for now: if a certain flag is set (this would usually cross-reference the finance engine)
        if hasattr(package, 'has_missing_payout') and package.has_missing_payout:
            return 'Payout Follow-up'
            
    # 6. Pending Daraz Decision
    if active_claim and active_claim.status in ['submitted', 'pending', 'appealed']:
        return 'Pending Daraz Decision'
        
    # 7. Pending Payout
    if active_claim and active_claim.status in ['approved', 'partially_approved']:
        return 'Pending Payout'
        
    # 8. Need Checking
    if dl_info['window_opened_at'] and not has_inspections:
        return 'Need Checking'
        
    # 9. In Transit To Seller
    if package.daraz_status == 'returning' and not dl_info['window_opened_at']:
        return 'In Transit To Seller'
        
    # 10. Pending Inspection Result (if inspection happened but waiting on something else internal)
    # Skipped or merged into Completed for now based on spec.
    
    # 11. Completed
    return 'Completed'
