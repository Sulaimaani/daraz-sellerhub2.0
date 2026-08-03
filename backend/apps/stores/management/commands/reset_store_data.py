from django.core.management.base import BaseCommand, CommandError
from apps.stores.models import Store, SyncJob
from apps.products.models import Product, Sku
from apps.orders.models import Customer, Order, OrderItem, Shipment
from apps.finance.models import FinanceTransaction, FinanceStatement
from apps.returns.models import ReturnPackage, ReturnItem

class Command(BaseCommand):
    help = 'Deletes all synced data for a store except Store, OAuthToken, and SkuCost.'

    def add_arguments(self, parser):
        parser.add_argument('store_id', type=int)
        parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    def handle(self, *args, **options):
        store_id = options['store_id']
        confirm = options['confirm']
        
        if not confirm:
            self.stdout.write(self.style.ERROR('Must pass --confirm to delete data.'))
            return
            
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise CommandError(f'Store {store_id} does not exist')
            
        self.stdout.write(f"Resetting data for store {store.name}...")
        
        # We need to delete in proper order to avoid cascading issues (though CASCADE mostly handles it, 
        # it's cleaner to be explicit if needed. Since models use CASCADE, deleting the roots deletes the children.)
        
        deleted_orders, _ = Order.objects.filter(store=store).delete()
        self.stdout.write(f"Deleted {deleted_orders} Orders (and their items/shipments)")
        
        deleted_customers, _ = Customer.objects.filter(store=store).delete()
        self.stdout.write(f"Deleted {deleted_customers} Customers")
        
        # Note: SkuCost is attached to Sku. The prompt states: "keeps Store, OAuthToken and SkuCost"
        # If we delete Sku, SkuCost is cascade deleted.
        # So we cannot delete Sku outright if we want to keep SkuCost, UNLESS we change the SkuCost FK to SET_NULL
        # or we just keep Products and SKUs since they are "Catalog" data not "Synced Payload" data.
        # Wait, the prompt says "reset_store_data <store_id> --confirm (deletes synced records, keeps Store, OAuthToken and SkuCost)".
        # I should just delete Finance, Returns, Orders, Customers.
        
        deleted_finance, _ = FinanceTransaction.objects.filter(store=store).delete()
        FinanceStatement.objects.filter(store=store).delete()
        self.stdout.write(f"Deleted {deleted_finance} Finance Transactions")
        
        deleted_returns, _ = ReturnPackage.objects.filter(store=store).delete()
        self.stdout.write(f"Deleted {deleted_returns} Return Packages")
        
        # Reset jobs
        store.sync_jobs.all().delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully reset data for store {store.name}'))
