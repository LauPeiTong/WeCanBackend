# order/models.py

from django.db import models
from users.models import Customer, Vendor
from products.models import Product

class Order(models.Model):
    DELIVERY_OR_PICKUP_CHOICES = [
        ('Delivery', 'Delivery'),
        ('Pick-up', 'Pick-up'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Delivering', 'Delivering'),
        ('Ready to Pick-up', 'Ready to Pick-up'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    delivery_or_pickup = models.CharField(max_length=10, choices=DELIVERY_OR_PICKUP_CHOICES, default='Delivery')
    notes = models.TextField(blank=True, null=True)
    products = models.ManyToManyField(Product, through='OrderItem')

    def calculate_total_price(self):
        # Calculate total price based on order items, fees, and taxes
        subtotal = 0
        total_price = 0
        for item in self.order_items.all():
            subtotal += item.product.price * item.quantity
        self.subtotal = subtotal
        
        if self.delivery_or_pickup == 'Delivery':
            total_price = self.delivery_fee + (self.tax * self.subtotal) + self.subtotal
        else:
            total_price = self.tax * self.subtotal + self.subtotal
        self.total_price = total_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity