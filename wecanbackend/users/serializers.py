from rest_framework import serializers
from .models import User, Vendor, Customer
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 'phone', 'address', 'city', 'image_url', 'latitude', 'longitude']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Extract the 'password' field from 'validated_data'
        password = validated_data.pop('password', None)

        # Create the user without setting the password yet
        user = User.objects.create(**validated_data)

        user.set_password(password)
        user.save()

        return user


class VendorSerializer(UserSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    rating = serializers.FloatField(default=0.0)
    display_name = serializers.CharField(required=False)
    category = serializers.CharField(required=False)

    class Meta:
        model = Vendor
        fields = UserSerializer.Meta.fields + ['tags', 'rating', 'display_name', 'category']

    def create(self, validated_data):
        # Extract and remove 'tags' from the validated_data
        tags = validated_data.pop('tags', [])
        password = validated_data.pop('password', None)

        # Create the Vendor instance with tags
        vendor = Vendor.objects.create(tags=tags, **validated_data)

        vendor.set_password(password)
        vendor.save()

        return vendor

class CustomerSerializer(UserSerializer):
    points = serializers.IntegerField(default=0)

    class Meta:
        model = Customer
        fields = UserSerializer.Meta.fields + ['points']

    def create(self, validated_data):
        # Create the Customer instance
        password = validated_data.pop('password', None)
        customer = Customer.objects.create(**validated_data)

        customer.set_password(password)
        customer.save()

        return customer
