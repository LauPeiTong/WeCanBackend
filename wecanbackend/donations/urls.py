# urls.py in your product app

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonationViewSet

router = DefaultRouter()
router.register(r'', DonationViewSet, basename='donation')

urlpatterns = [
    path('', include(router.urls)),
]
