from django.urls import path

from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserListView, VendorListView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
]
