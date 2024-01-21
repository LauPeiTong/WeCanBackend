# order/urls.py

from django.urls import path
from .views import OrderListCreateView, OrderRetrieveUpdateView, CustomerOrderItemsStatusView, OrderSummaryView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('<int:pk>/', OrderRetrieveUpdateView.as_view(), name='order-retrieve-update'),
    # path('order-items/', CustomerOrderItemsView.as_view(), name='customer-order-items'),
    path('order-items-status/', CustomerOrderItemsStatusView.as_view(), name='customer-order-items-status'),
    # Add more URLs as needed
]