import os
import json
import random

from django.core.management.base import BaseCommand
from users.models import Vendor
from products.models import Product
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

tag_choices = ['Halal', 'Western', 'Chinese', 'Menu Rahmah', 'Free Delivery']


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'info_menu.json')

        with open(file_path, 'r') as file:
            data = json.load(file)


        for vendor in data:
            username = vendor['code']

            # Check if a vendor with the given username already exists
            existing_vendor = Vendor.objects.filter(username=username).first()

            if existing_vendor is None:
                # If the username does not exist, create a new vendor
                new_vendor = Vendor.objects.create(
                    username=username,
                    password='testing/123',
                    display_name=vendor['name'],
                    email=fake.email(),
                    role='V',
                    phone=fake.phone_number(),
                    address=vendor['address'],
                    city=vendor['city']['name'],
                    latitude=vendor['city']['latitude'],
                    longitude=vendor['city']['longitude'],
                    image_url=vendor['hero_listing_image'],
                    rating=vendor['rating'],
                    tags=self.generate_random_tags()
                )

                for product in vendor['menus'][0]['menu_categories']:
                    d = product['description']

                    for p in product['products']:
                        Product.objects.create(
                            vendor=new_vendor,
                            name=p['name'],
                            original_price=p['product_variations'][0]['price'],
                            discount=self.generate_random_discount_amount(),
                            expired_date=self.generate_random_expiry_date(),
                            image_url=p['logo_path'],
                            description=d,
                            nutrients='',
                            quantity=self.generate_random_quantity(),
                        )


    
    def generate_random_tags(self): 
        num_tags = random.randint(0, 2)

        # Randomly select tags
        selected_tags = random.sample(tag_choices, num_tags)

        return selected_tags

    def generate_random_discount_amount(self):
        discount_options = [20, 25, 40, 50, 75]
        return random.choice(discount_options)

    def generate_random_quantity(self):
        return random.randint(1, 20)

    def generate_random_expiry_date(self):
        # Get today's date
        today = datetime.now()

        # Generate a random number of days between 0 and 14 (2 weeks)
        random_days = random.randint(0, 14)

        # Calculate the future date
        expiry_date = today + timedelta(days=random_days)

        # Set the time to 11:59:59 PM
        expiry_date = expiry_date.replace(hour=23, minute=59, second=59, microsecond=0)

        # Format the date in 'YYYY-MM-DDTHH:MM:SS' format
        formatted_expiry_date = expiry_date.strftime('%Y-%m-%dT%H:%M:%S')

        return formatted_expiry_date