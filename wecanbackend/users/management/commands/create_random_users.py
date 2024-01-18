import random
from faker import Faker
from django.contrib.auth import get_user_model
from users.models import Customer
from django.core.management.base import BaseCommand
import requests

fake = Faker()

User = get_user_model()

class Command(BaseCommand):
    help = 'Create random customer data'

    def handle(self, *args, **options):
        # Generate 50 random customers
        for _ in range(5):
            new_customer = Customer.objects.create(
                username=fake.user_name(),
                password='testing/123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                role='C',
                phone=self.generate_malaysian_phone_number(),
                address='Putrajaya, Malaysia',
                image_url='https://www.shareicon.net/data/512x512/2017/01/06/868271_user_512x512.png',
                points=random.randint(0, 1000)
            )

            if new_customer.address:
                # Replace 'YOUR_OPENCAGE_API_KEY' with your actual OpenCageData API key
                opencage_api_key = 'ac8dde804c164035951250eca1859dae'
                opencage_url = f'https://api.opencagedata.com/geocode/v1/json?q={new_customer.address}&key={opencage_api_key}'

                response = requests.get(opencage_url)
                data = response.json()

                if 'results' in data and len(data['results']) > 0:
                    geometry = data['results'][0]['geometry']
                    new_customer.latitude = geometry['lat']
                    new_customer.longitude = geometry['lng']

            new_customer.set_password('testing/123')
            new_customer.save()


    def generate_malaysian_phone_number(self):
        # Generate a random number with 9 digits
        random_number = fake.random_number(digits=9)

        # Convert the integer to a string
        random_number_str = str(random_number)

        # Format it to look like a Malaysian phone number
        formatted_number = f"01{random_number_str[:1]}-{random_number_str[1:4]} {random_number_str[4:7]}"
        return formatted_number