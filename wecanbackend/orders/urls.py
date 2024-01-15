# order/urls.py

from django.urls import path
from .views import OrderListCreateView, OrderRetrieveUpdateView, CustomerOrderItemsView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderRetrieveUpdateView.as_view(), name='order-retrieve-update'),
    path('order-items/', CustomerOrderItemsView.as_view(), name='customer-order-items'),
    # Add more URLs as needed
]