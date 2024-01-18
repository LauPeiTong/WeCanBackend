from django.db import models
from users.models import Customer


class Donation(models.Model):
    TYPE_CHOICES = [
        ('Round-up', 'Round-up'),
        ('Points', 'Points'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Points')
