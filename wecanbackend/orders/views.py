# order/views.py

from rest_framework import generics, permissions
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, CustomerOrderItemSerializer
from .permissions import IsCustomerOrVendor
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'C':
            return Order.objects.filter(customer=user.customer)
        elif user.role == 'V':
            return Order.objects.filter(vendor=user.vendor)
        elif user.role == 'A':
            return Order.objects.all()
        else:
            raise PermissionDenied("User does not have the required role for this operation.")
        
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class OrderRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrVendor]

    def perform_update(self, serializer):
        user = self.request.user
        if user.role == 'C':
            raise PermissionDenied("Customers are not allowed to update orders.")
        serializer.save()


class CustomerOrderItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Assuming you have some way to identify the customer, e.g., through authentication
        user = request.user  # Replace this with your actual way of getting the customer

        if user.role == 'C':
            # Retrieve all OrderItems for the customer
            order_items = OrderItem.objects.filter(order__customer=user.customer)

            # Serialize the data
            serializer = CustomerOrderItemSerializer(order_items, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        raise PermissionDenied("User does not have the required role for this operation.")