from django.core.management.base import BaseCommand, CommandError
from apps.stores.models import Store, SyncJob
from apps.stores.tasks import start_history_import

class Command(BaseCommand):
    help = 'Triggers a full 120-day history rebuild for a store.'

    def add_arguments(self, parser):
        parser.add_argument('store_id', type=int)

    def handle(self, *args, **options):
        store_id = options['store_id']
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise CommandError(f'Store {store_id} does not exist')
            
        active_jobs = store.sync_jobs.filter(status__in=[SyncJob.Status.QUEUED, SyncJob.Status.RUNNING]).exists()
        if active_jobs:
            self.stdout.write(self.style.ERROR('A sync job is already running for this store.'))
            return
            
        start_history_import.delay(store.id)
        self.stdout.write(self.style.SUCCESS(f'Successfully queued history rebuild for store {store.name}'))
