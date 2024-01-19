from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Vendor

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_staff', 'is_superuser')

admin.site.register(User, CustomUserAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'latitude', 'longitude', 'email', 'points')  # Include other fields you want to display
    search_fields = ('username', 'email')  # Search fields in the related User model

admin.site.register(Customer, CustomerAdmin, name='Customer')

class VendorAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'display_name', 'email', 'city', 'rating', 'get_tags_display')  # Include other fields you want to display
    search_fields = ('username', 'email')  # Search fields in the related User model

admin.site.register(Vendor, VendorAdmin,name='Vendor')
