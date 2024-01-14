# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from geopy.distance import geodesic

class User(AbstractUser):
    CHOICES = (
        ('C', 'Customer'),
        ('V', 'Vendor'),
        ('A', 'Admin')
    )

    role = models.CharField(max_length=15, choices=CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)


class Vendor(User):
    # additional fields specific to vendors
    tags = models.JSONField(default=list)  # Storing tags as a list of strings
    rating = models.FloatField(default=0.0)

    def distance_to_customer(self, customer_latitude, customer_longitude):
        vendor_location = (self.latitude, self.longitude)
        customer_location = (customer_latitude, customer_longitude)
        return geodesic(customer_location, vendor_location).kilometers
    
    def get_tags_display(self):
        return ', '.join(self.tags)

class Customer(User):
    # additional fields specific to customers
    points = models.IntegerField(default=0)
