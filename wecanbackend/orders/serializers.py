# order/serializers.py

from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer

from rest_framework import serializers


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class CustomerOrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        order_items_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for item_data in order_items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            product = Product.objects.get(id=product.id)
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

            product.quantity -= quantity
            product.save()
        
        order.calculate_total_price()
        order.save()

        return order

    def update(self, instance, validated_data):
        # Allow updating only the 'status' field
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance





