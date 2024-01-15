# models.py in your product app

from django.db import models
from users.models import Vendor
from django.utils import timezone


class Product(models.Model):
    STATUS_CHOICES = [
        ('Expired', 'Expired'),
        ('Within Shelf Life', 'Within Shelf Life'),
        ('Near Expiry', 'Near Expiry'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)
    nutrients = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Within Shelf Life')
    
    @property
    def price(self):
        # Calculate the discounted price
        discounted_amount = self.original_price * (self.discount / 100)
        discounted_price = self.original_price - discounted_amount
        return discounted_price

    @property
    def time_left(self):
        now = timezone.now()
        time_difference = self.expired_date - now

        # Check if the product is expired
        if time_difference.total_seconds() <= 0:
            return {
                'hours': 0,
                'days': 0,
                'status': 'Expired'
            }
        # Check if the product is near expiry (less than 1 day)
        elif time_difference.total_seconds() < 86400:  # 86400 seconds in a day
            return {
                'hours': time_difference.total_seconds() // 3600,
                'days': time_difference.days,
                'status': 'Near Expiry'
            }
        else:
            return {
                'hours': time_difference.total_seconds() // 3600,
                'days': time_difference.days,
                'status': 'Within Shelf Life'
            }

    def save(self, *args, **kwargs):
        # Automatically set the status when saving a new product
        if not self.id:
            time_left_info = self.time_left
            self.status = time_left_info.get('status', 'Within Shelf Life')

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
