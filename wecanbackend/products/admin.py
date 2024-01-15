# admin.py in your product app

from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'vendor', 'original_price', 'discount', 'price', 'quantity', 'created_at', 'expired_date', 'status')
    search_fields = ('name', 'vendor__username', 'created_at', 'expired_date')
    list_filter = ('vendor__username', 'status', 'expired_date')
    ordering = ('-created_at',)
