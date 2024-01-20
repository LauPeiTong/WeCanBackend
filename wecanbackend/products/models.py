# models.py in your product app

from django.db import models
from users.models import Vendor
from django.utils import timezone
from datetime import datetime
import pytz


class Product(models.Model):
    STATUS_CHOICES = [
        ('Expired', 'Expired'),
        ('Within Shelf Life', 'Within Shelf Life'),
        ('Near Expiry', 'Near Expiry'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)
    nutrients = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Within Shelf Life')
    category = models.CharField(max_length=255, default='Food', blank=True, null=True)
    
    @property
    def price(self):
        # Calculate the discounted price
        discounted_amount = self.original_price * (self.discount / 100)
        discounted_price = self.original_price - discounted_amount
        return discounted_price
    
    @property
    def time_left(self):
        kl_timezone = pytz.timezone('Asia/Kuala_Lumpur')
        # expired_date = kl_timezone.localize(datetime.strptime(self.expired_date, '%Y-%m-%dT%H:%M:%S'))
        expired_date = self.expired_date

        # Get the current datetime in Kuala Lumpur timezone
        now = datetime.now(kl_timezone)

        # Calculate the time difference
        time_difference = expired_date - now

        # Update the status based on the current time
        new_status = ''
        if time_difference.total_seconds() <= 0:
            new_status = 'Expired'
        elif time_difference.total_seconds() < 86400:  # 86400 seconds in a day
            new_status = 'Near Expiry'
        else:
            new_status = 'Within Shelf Life'

        # Check if the status has changed before saving
        if self.id and self.status != new_status:
            self.status = new_status
            self.save()

        return {
            'hours': time_difference.total_seconds() // 3600,
            'days': time_difference.days,
            'status': new_status
        }

    
    def save(self, *args, **kwargs):
        # Automatically set the status when saving a new product
        if not self.id:
            time_left_info = self.time_left
            self.status = time_left_info.get('status', 'Within Shelf Life')

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
