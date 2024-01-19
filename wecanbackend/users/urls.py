from django.urls import path, include

from .views import UserRegistrationView, UserLoginView, UserLogoutView, VendorListView, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
]
