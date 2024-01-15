import random
from faker import Faker
from django.contrib.auth import get_user_model
from users.models import Customer
from django.core.management.base import BaseCommand

fake = Faker()

User = get_user_model()

class Command(BaseCommand):
    help = 'Create random customer and vendor data'

    def handle(self, *args, **options):
        selangor_kl_location = {
            'latitude': 3.3358,  # Replace with the actual latitude of Selangor
            'longitude': 101.9717  # Replace with the actual longitude of Selangor
        }

        # Generate 50 random customers
        for _ in range(5):
            Customer.objects.create(
                username=fake.user_name(),
                password='testing/123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                role='C',
                phone=fake.phone_number(),
                address='Damansara Damai, 47830 Petaling Jaya, Selangor, Malaysia',
                image_url='https://th.bing.com/th/id/OIP.3hkA5Yx5YUpUMtbsaioJggAAAA?rs=1&pid=ImgDetMain',
                points=random.randint(0, 1000)
            )
