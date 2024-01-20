import random
from django.core.management.base import BaseCommand
from users.models import Customer
from donations.models import Donation
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate random donations for type "Points"'

    ORGANIZATION_NAMES = [
        'WeCan Project',
        'The Lost Food Project',
        'Food Aid Foundation',
        'Malaysian Red Crescent Society (Food Aid Program)',
        'Yayasan Food Bank Malaysia',
        'Kechara Soup Kitchen'
    ]

    def handle(self, *args, **options):
        # Get all customers
        customers = Customer.objects.all()

        # Generate 200 random donations for type 'Points'
        for _ in range(200):
            customer = random.choice(customers)
            organization_name = random.choice(self.ORGANIZATION_NAMES)
            amount = random.choice([5, 10, 20, 30])

            # Generate a random date within the last 30 days
            created_at = datetime.now() - timedelta(days=random.randint(0, 30))

            # Create Donation instance
            donation = Donation.objects.create(
                customer=customer,
                organization_name=organization_name,
                amount=amount,
                created_at=created_at,
                type='Points',
            )

            created_at = created_at.replace(
                hour=random.randint(7, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=0  # Reset microsecond to 0
            )

            donation.created_at = created_at
            donation.save()

        self.stdout.write(self.style.SUCCESS('Successfully generated random donations for type "Points".'))
