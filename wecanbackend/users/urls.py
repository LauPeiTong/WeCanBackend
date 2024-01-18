from django.urls import path, include

from .views import UserRegistrationView, UserLoginView, UserLogoutView, VendorListView, UserListView
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
]
