# run python manage.py seed_job_db

from django.core.management.base import BaseCommand
from Jobapp.models import Company,Job,User as UserProfile  # Import your model
from Jobapp.seed import company_data,job_data,user_prof_data  # Import your seed data

class Command(BaseCommand):
    help = 'Populate the database with seed data'

    def handle(self, *args, **options):
        for data in company_data:
            Company.objects.create(**data).save()
        
        for data in job_data:
            Job.objects.create(**data).save()

        for data in user_prof_data:
            UserProfile.objects.create(**data).save()
        self.stdout.write(self.style.SUCCESS('Successfully seeded the jobapp data in database'))
