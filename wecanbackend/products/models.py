# models.py in your product app

from django.db import models
from users.models import Vendor


class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)
    nutrients = models.TextField(blank=True, null=True)
    
    @property
    def price(self):
        # Calculate the discounted price
        discounted_amount = self.original_price * (self.discount / 100)
        discounted_price = self.original_price - discounted_amount
        return discounted_price

    def __str__(self):
        return self.name
