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

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15, choices=CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)


class Vendor(User):
    CHOICES = (
        ('Restaurant', 'Restaurant'),
        ('Supermarket', 'Supermarket'),
        ('Grocery', 'Grocery'),
        ('Bakery', 'Bakery')
    )
    
    # additional fields specific to vendors
    tags = models.JSONField(default=list)  # Storing tags as a list of strings
    rating = models.FloatField(default=0.0)
    display_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=CHOICES)

    def distance_to_customer(self, customer_latitude, customer_longitude):
        vendor_location = (self.latitude, self.longitude)
        customer_location = (customer_latitude, customer_longitude)
        return geodesic(customer_location, vendor_location).kilometers
    
    def get_tags_display(self):
        return ', '.join(self.tags)

class Customer(User):
    # additional fields specific to customers
    points = models.IntegerField(default=0)
