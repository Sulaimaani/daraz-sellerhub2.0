from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from apps.stores.models import Store
from apps.orders.sync import sync_orders_window, sync_finance_window, sync_returns_window, sync_products_window

class Command(BaseCommand):
    help = 'Manually syncs a specific resource for a store over N days.'

    def add_arguments(self, parser):
        parser.add_argument('store_id', type=int)
        parser.add_argument('--resource', type=str, required=True, choices=['orders', 'finance', 'returns', 'products'])
        parser.add_argument('--days', type=int, default=7)

    def handle(self, *args, **options):
        store_id = options['store_id']
        resource = options['resource']
        days = options['days']
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise CommandError(f'Store {store_id} does not exist')
            
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(f"Starting {resource} sync for store {store.name} from {start_date} to {end_date}...")
        
        if resource == 'products':
            sync_products_window(store)
        elif resource == 'orders':
            sync_orders_window(store, start_date, end_date)
        elif resource == 'finance':
            sync_finance_window(store, start_date, end_date)
        elif resource == 'returns':
            sync_returns_window(store)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully completed {resource} sync'))
