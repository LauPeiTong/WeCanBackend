# serializers.py in your product app

from rest_framework import serializers

# from users.serializers import VendorSerializer
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    # vendor = VendorSerializer()
    time_left = serializers.SerializerMethodField()
    price = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_time_left(self, obj):
        return obj.time_left
