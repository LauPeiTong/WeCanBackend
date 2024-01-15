# urls.py in your product app

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, VendorProductsViewSet

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')
router.register(r'vendor/(?P<vendor_id>\d+)', VendorProductsViewSet, basename='vendor-products')

urlpatterns = [
    path('', include(router.urls)),
]
