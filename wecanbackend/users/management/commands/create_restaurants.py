import os
import json
import random

from django.core.management.base import BaseCommand
from users.models import Vendor
from products.models import Product
from faker import Faker
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pytz

fake = Faker()

tag_choices = ['Halal', 'Western', 'Chinese', 'Menu Rahmah', 'Free Delivery']


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'info_menu.json')

        with open(file_path, 'r') as file:
            data = json.load(file)


        for vendor in data:
            username = vendor['code']
            klang_valley_cities = [
                ["Shah Alam", "Selangor, Malaysia"],
                ["Subang Jaya", "Selangor, Malaysia"],
                ["Klang", "Selangor, Malaysia"], 
                ["Kajang", "Selangor, Malaysia"], 
                ["Rawang", "Selangor, Malaysia"], 
                ["Sungai Buloh", "Selangor, Malaysia"],
                ["Serdang", "Selangor, Malaysia"],
                ["Kepong", "Kuala Lumpur, Malaysia"],
                ["Bukit Bintang", "Kuala Lumpur, Malaysia"],
                ["Cheras", "Kuala Lumpur, Malaysia"],
                ["Damansara", "Kuala Lumpur, Malaysia"],
                ["Mont Kiara", "Kuala Lumpur, Malaysia"],
                ["Bangsar", "Kuala Lumpur, Malaysia"],
                ["Sentul", "Kuala Lumpur, Malaysia"],
                ["Wangsa Maju", "Kuala Lumpur, Malaysia"],
                ["Titiwangsa", "Kuala Lumpur, Malaysia"],
                ["Putrajaya", "Malaysia"]
            ]
            random_city = random.choice(klang_valley_cities)
            coordinates = self.get_coordinates(random_city[0])

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
                    phone=self.generate_malaysian_phone_number(),
                    address=vendor['address'],
                    city=vendor['city']['name'],
                    latitude=vendor['latitude'],
                    longitude=vendor['longitude'],
                    image_url=vendor['hero_listing_image'],
                    rating=vendor['rating'],
                    tags=self.generate_random_tags(),
                    category='Restaurant'
                )

                new_vendor_2 = Vendor.objects.create(
                    username=username + '2',
                    password='testing/123',
                    display_name=fake.company(),
                    email=fake.email(),
                    role='V',
                    phone=self.generate_malaysian_phone_number(),
                    address=random_city[0] + ", " + random_city[1],
                    city=random_city[0],
                    latitude=coordinates[0],
                    longitude=coordinates[1],
                    image_url=vendor['hero_image'],
                    rating=vendor['rating'],
                    tags=self.generate_random_tags(),
                    category='Restaurant'
                )

                new_vendor_3 = Vendor.objects.create(
                    username=username + '3',
                    password='testing/123',
                    display_name=fake.company(),
                    email=fake.email(),
                    role='V',
                    phone=self.generate_malaysian_phone_number(),
                    address=random_city[0] + ", " + random_city[1],
                    city=random_city[0],
                    latitude=coordinates[0],
                    longitude=coordinates[1],
                    image_url=vendor['hero_listing_image'],
                    rating=vendor['rating'],
                    tags=self.generate_random_tags(),
                    category='Restaurant'
                )

                new_vendor.set_password('testing/123')
                new_vendor.save()

                new_vendor_2.set_password('testing/123')
                new_vendor_2.save()

                new_vendor_3.set_password('testing/123')
                new_vendor_3.save()

                for product in vendor['menus'][0]['menu_categories']:

                    for i, p in enumerate(product['products']):
                        # Check if the index is less than half the length

                        if i % 3 == 0:
                            Product.objects.create(
                                vendor=new_vendor,
                                name=p['name'],
                                original_price=p['product_variations'][0]['price'],
                                discount=self.generate_random_discount_amount(),
                                expired_date=self.generate_random_expiry_date(),
                                image_url=p['logo_path'],
                                description=p['description'],
                                nutrients='',
                                quantity=self.generate_random_quantity(),
                                category=product['name']
                            )
                        elif i % 3 == 1:
                            Product.objects.create(
                                vendor=new_vendor_2,
                                name=p['name'],
                                original_price=p['product_variations'][0]['price'],
                                discount=self.generate_random_discount_amount(),
                                expired_date=self.generate_random_expiry_date(),
                                image_url=p['logo_path'],
                                description=p['description'],
                                nutrients='',
                                quantity=self.generate_random_quantity(),
                                category=product['name']
                            )
                        else:
                            Product.objects.create(
                                vendor=new_vendor_3,
                                name=p['name'],
                                original_price=p['product_variations'][0]['price'],
                                discount=self.generate_random_discount_amount(),
                                expired_date=self.generate_random_expiry_date(),
                                image_url=p['logo_path'],
                                description=p['description'],
                                nutrients='',
                                quantity=self.generate_random_quantity(),
                                category=product['name']
                            )
            # else:
            #     existing_vendor.set_password('testing/123')
            #     existing_vendor.save()
                # existing_vendor.phone=self.generate_malaysian_phone_number()
                # print(existing_vendor.phone)
                # existing_vendor.save()
                # existing_vendor.latitude=vendor['latitude']
                # existing_vendor.longitude=vendor['longitude']
                # existing_vendor.category='Restaurant'
                # existing_vendor.save()


    def generate_random_tags(self): 
        num_tags = random.randint(0, 2)

        # Randomly select tags
        selected_tags = random.sample(tag_choices, num_tags)

        return selected_tags
    
    def generate_malaysian_phone_number(self):
        # Generate a random number with 9 digits
        random_number = fake.random_number(digits=9)

        # Convert the integer to a string
        random_number_str = str(random_number)

        # Format it to look like a Malaysian phone number
        formatted_number = f"01{random_number_str[:1]}-{random_number_str[1:4]} {random_number_str[4:7]}"
        return formatted_number

    def generate_random_discount_amount(self):
        discount_options = [20, 25, 40, 50, 75]
        return random.choice(discount_options)

    def generate_random_quantity(self):
        return random.randint(1, 20)

    def generate_random_expiry_date(self):
        # Get today's date
        today = datetime.now()

        # Generate a random number of days between 0 and 14 (2 weeks)
        random_days = random.randint(-30, 7)

        # Calculate the future date
        expiry_date = today + timedelta(days=random_days)

        # Set the time to 11:59:59 PM
        expiry_date = expiry_date.replace(hour=23, minute=59, second=59, microsecond=0)

        # Format the date in 'YYYY-MM-DDTHH:MM:SS' format
        formatted_expiry_date = expiry_date.strftime('%Y-%m-%dT%H:%M:%S')

        kl_timezone = pytz.timezone('Asia/Kuala_Lumpur')
        formatted_expiry_date = kl_timezone.localize(datetime.strptime(formatted_expiry_date, '%Y-%m-%dT%H:%M:%S'))

        return formatted_expiry_date
    
    def get_coordinates(self, city):

        geolocator = Nominatim(user_agent="city-coordinates")
        location = geolocator.geocode(f"{city}, Selangor, Malaysia")

        if location:
            latitude, longitude = location.latitude, location.longitude
            return latitude, longitude
        else:
            return 3.162215, 101.586932
