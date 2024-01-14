from rest_framework import serializers
from .models import User, Vendor, Customer

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password', 'phone', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class VendorSerializer(UserSerializer):
    tags = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    rating = serializers.FloatField(default=0.0)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Vendor
        fields = UserSerializer.Meta.fields + ['tags', 'rating', 'latitude', 'longitude']

    def create(self, validated_data):
        # Extract and remove 'tags' from the validated_data
        tags = validated_data.pop('tags', [])

        # Create the Vendor instance with tags
        vendor = Vendor.objects.create(tags=tags, **validated_data)

        return vendor

class CustomerSerializer(UserSerializer):
    points = serializers.IntegerField(default=0)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Customer
        fields = UserSerializer.Meta.fields + ['points', 'latitude', 'longitude']

    def create(self, validated_data):
        # Create the Customer instance
        customer = Customer.objects.create(**validated_data)

        return customer
