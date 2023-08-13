# run python manage.py seed_account_db

from django.core.management.base import BaseCommand
from accountapp.models import User  # Import your model
from accountapp.seed import user_data  # Import your seed data

class Command(BaseCommand):
    help = 'Populate the database with seed data'

    def handle(self, *args, **options):
        for data in user_data:
            User.objects.create(**data).save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded the account data in database'))
