# admin.py in your product app

from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_name', 'amount', 'created_at', 'customer')
    search_fields = ('customer__username', 'created_at', 'organization_name')
    list_filter = ('customer__username', 'created_at', 'organization_name')
    ordering = ('-created_at',)
