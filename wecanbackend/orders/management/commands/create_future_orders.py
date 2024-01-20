import random
from faker import Faker
from users.models import Customer, Vendor
from donations.models import Donation
from products.models import Product
from orders.models import Order, OrderItem
from django.db import transaction
from django.core.management.base import BaseCommand
from decimal import Decimal
from datetime import datetime, timedelta

fake = Faker()

STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('To Receive', 'To Receive'),
        ('Completed', 'Completed')
    ]

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get existing customers and vendors
        customers = Customer.objects.all()
        vendors = Vendor.objects.all()

        # Loop through the last 30 days starting from today and going backward until January 23rd
        today = datetime.now()
        end_date = datetime(2024, 1, 23)  # Change the date accordingly

        # Make sure end_date is at most 30 days before today
        end_date = min(end_date, today - timedelta(days=30))

        start_date = today - timedelta(days=29)

        while start_date >= end_date:
            # Your existing code for each iteration

            # Generate fake orders using existing customers and vendors for each day
            for _ in range(random.randint(1, 5)):
                customer = random.choice(customers)
                vendor = random.choice(vendors)
                self.generate_fake_order(customer, vendor, start_date)

            # Move to the previous day
            start_date -= timedelta(days=1)

    def generate_fake_order(self, customer, vendor, order_created_at):
        with transaction.atomic():
            order_choice = random.choice([choice[0] for choice in Order.DELIVERY_OR_PICKUP_CHOICES])
            status_choice = random.choice([choice[0] for choice in STATUS_CHOICES])
            if order_choice == 'Delivery':
                fee = random.randint(0, 15)
            else:
                fee = 0
            
            # Random decision for round_up
            round_up_decision = random.choice([True, True, False])

            # Get the products associated with the vendor
            vendor_products = Product.objects.filter(vendor=vendor, expired_date__date=order_created_at.date())

            # Check if there are any products available
            if not vendor_products.exists():
                # No products available, skip order creation
                return
            
            # Manually set the created_at field to the generated date
            order = Order.objects.create(
                customer=customer,
                vendor=vendor,
                delivery_fee=Decimal(str(fee)),
                tax=Decimal(str(0.05)),
                status=status_choice,
                delivery_or_pickup=order_choice,
                notes='',
                round_up=0,
                created_at=order_created_at,
            )

            # Randomly determine the number of products to add to the order
            num_products = random.randint(1, min(5, len(vendor_products)))

            # Choose a random subset of products
            selected_products = random.sample(list(vendor_products), num_products)

            for product in selected_products:
                # Ensure product.quantity is greater than 0
                if product.quantity > 0:
                    quantity = random.randint(1, min(2, product.quantity))
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)

                    # Decrease product.quantity by the ordered quantity
                    product.quantity -= quantity
                    product.save()

            # Calculate and save the total price
            order.calculate_total_price()

            # Assign a random time within the given date
            order_created_at = order_created_at.replace(
                hour=random.randint(7, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=0  # Reset microsecond to 0
            )

            order.created_at = order_created_at

            if round_up_decision:
                order.calculate_round_up()

                donation = Donation.objects.create(
                    customer=customer,
                    organization_name='WeCan Project',
                    amount=order.round_up,
                    type='Round-up',
                    order=order,
                    created_at=order_created_at
                )

                donation.created_at = order_created_at
                donation.save()

            order.save()

    # Other methods remain unchanged
