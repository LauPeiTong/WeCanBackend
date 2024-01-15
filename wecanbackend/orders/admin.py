from django.contrib import admin
from .models import Order, OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'vendor', 'delivery_fee', 'tax', 'total_price', 'status', 'delivery_or_pickup', 'notes', 'created_at']
    list_filter = ['status', 'delivery_or_pickup']
    search_fields = ['customer__username', 'vendor__username', 'id']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'order']
    search_fields = ['id']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin, name="Items")