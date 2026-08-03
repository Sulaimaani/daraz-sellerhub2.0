import datetime
from django.utils import timezone
from .models import Holiday

def is_business_day(date_obj):
    # Weekends in PK typically Sat/Sun (or Sun for some, but typically Sat/Sun for Daraz 5-day SLA)
    if date_obj.weekday() >= 5: # 5=Sat, 6=Sun
        return False
    # Check holidays
    if Holiday.objects.filter(date=date_obj.date()).exists():
        return False
    return True

def add_business_days(start_date, days_to_add):
    current_date = start_date
    while days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        if is_business_day(current_date):
            days_to_add -= 1
    return current_date

def calculate_deadline(package):
    """
    Returns dict: window_opened_at, window_closes_at, business_days_left, is_overdue, source_field, confidence
    Preferred source: returned_at -> daraz_status_updated_at -> received_at
    """
    source_field = None
    window_opened_at = None
    
    if package.returned_at:
        source_field = 'returned_at'
        window_opened_at = package.returned_at
    elif package.daraz_status_updated_at and package.daraz_status == 'returned':
        source_field = 'daraz_status_updated_at'
        window_opened_at = package.daraz_status_updated_at
    elif package.received_at:
        source_field = 'received_at'
        window_opened_at = package.received_at
        
    if not window_opened_at:
        return {
            'window_opened_at': None,
            'window_closes_at': None,
            'business_days_left': 0,
            'is_overdue': False,
            'source_field': None,
            'confidence': 'low',
            'error': 'needs_data_review'
        }
        
    window_closes_at = add_business_days(window_opened_at, 5)
    
    now = timezone.now()
    
    # Calculate days left
    business_days_left = 0
    temp_date = now
    
    if temp_date < window_closes_at:
        while temp_date.date() < window_closes_at.date():
            temp_date += datetime.timedelta(days=1)
            if is_business_day(temp_date):
                business_days_left += 1
    else:
        # Overdue
        while temp_date.date() > window_closes_at.date():
            temp_date -= datetime.timedelta(days=1)
            if is_business_day(temp_date):
                business_days_left -= 1
                
    is_overdue = now > window_closes_at
    
    return {
        'window_opened_at': window_opened_at,
        'window_closes_at': window_closes_at,
        'business_days_left': business_days_left,
        'is_overdue': is_overdue,
        'source_field': source_field,
        'confidence': 'high'
    }
