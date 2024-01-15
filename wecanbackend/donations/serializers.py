# serializers.py in your product app

from rest_framework import serializers

# from users.serializers import VendorSerializer
from .models import Donation

class DonationSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Donation
        fields = '__all__'
