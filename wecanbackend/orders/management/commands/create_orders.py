import random
from faker import Faker
from users.models import Customer, Vendor
from products.models import Product
from orders.models import Order, OrderItem
from django.db import transaction
from django.core.management.base import BaseCommand
from decimal import Decimal
from datetime import datetime, timedelta

fake = Faker()

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get existing customers and vendors
        customers = Customer.objects.all()
        vendors = Vendor.objects.all()

        # Generate 10 fake orders using existing customers and vendors
        for _ in range(10):
            customer = random.choice(customers)
            vendor = random.choice(vendors)
            self.generate_fake_order(customer, vendor)

    def generate_fake_order(self, customer, vendor):
        with transaction.atomic():
            # Generate a random date within the past month
            order_created_at = self.generate_random_past_date()

            order_choice = random.choice([choice[0] for choice in Order.DELIVERY_OR_PICKUP_CHOICES])
            status_choice = random.choice([choice[0] for choice in Order.STATUS_CHOICES])
            if order_choice == 'Delivery':
                fee = random.randint(0, 15)
                if status_choice == 'Ready to Pick-up':
                    status_choice = 'Delivering'
            else:
                fee = 0
                if status_choice == 'Delivering':
                    status_choice = 'Ready to Pick-up'

            # Manually set the created_at field to the generated date
            order = Order.objects.create(
                customer=customer,
                vendor=vendor,
                delivery_fee=Decimal(str(fee)),
                tax=Decimal(str(0.05)),
                status=status_choice,
                delivery_or_pickup=order_choice,
                notes='',
            )
            order.created_at = order_created_at
            order.save()
            print(order_created_at)

            # Get the products associated with the vendor
            vendor_products = Product.objects.filter(vendor=vendor, expired_date__date=order_created_at.date())

            # Generate fake order items
            for _ in range(random.randint(1, 5)):
                product = random.choice(vendor_products)

                # Ensure product.quantity is greater than 0
                if product.quantity > 0:
                    quantity = random.randint(1, min(2, product.quantity))
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)

                    # Decrease product.quantity by the ordered quantity
                    product.quantity -= quantity
                    product.save()

            # Calculate and save the total price
            order.calculate_total_price()
            order.save()

    def generate_random_past_date(self):
        # Generate a random number of days between 0 and 30
        random_days = random.randint(0, 30)

        # Calculate the past date
        past_date = datetime.now() - timedelta(days=random_days)

        return past_date
