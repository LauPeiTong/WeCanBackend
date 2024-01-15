from django.db import models
from users.models import Customer


class Donation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
