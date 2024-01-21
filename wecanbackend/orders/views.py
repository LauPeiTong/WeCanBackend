# order/views.py

from rest_framework import generics, permissions
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, CustomerOrderItemSerializer
from .permissions import IsCustomerOrVendor
from users.serializers import VendorSerializer, CustomerSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10  # Number of donations to be displayed per page
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Maximum number of donations that can be requested per page


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        user = self.request.user
    
        if user.role == 'C':
            orders = Order.objects.filter(customer=user.customer)
        elif user.role == 'V':
            orders = Order.objects.filter(vendor=user.vendor)
        elif user.role == 'A':
            orders = Order.objects.all()
        else:
            raise PermissionDenied("User does not have the required role for this operation.")
        
        return orders

    def list(self, request, *args, **kwargs):
        # Call super().list to get the default paginated response
        response = super().list(request, *args, **kwargs)

        orders_with_extra_data = []
        for order_data in response.data['results']:
            order = Order.objects.get(pk=order_data['id'])  # Retrieve the Order object
            if order.vendor:
                vendor_serializer = VendorSerializer(order.vendor)
                vendor_data = vendor_serializer.data
                order_data['vendor'] = vendor_data
                
            if order.customer:
                customer_serializer = CustomerSerializer(order.customer)
                customer_data = customer_serializer.data
                order_data['customer'] = customer_data

            orders_with_extra_data.append(order_data)

        # Modify the response data with the additional information
        response.data['results'] = orders_with_extra_data

        # Return the response with the modified data
        return response
                
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)

        customer = self.request.user.customer

        points_earned = self.request.data.get('points', 0)

        # Update the customer's points
        customer.points += points_earned

        # Save the updated customer
        customer.save()


class OrderSummaryView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
    
        if user.role == 'C':
            orders = Order.objects.filter(customer=user.customer)
        elif user.role == 'V':
            orders = Order.objects.filter(vendor=user.vendor)
        elif user.role == 'A':
            orders = Order.objects.all()
        else:
            raise PermissionDenied("User does not have the required role for this operation.")
        
        return orders

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        result = {'Pending': [], 'Processing': [], 'To Receive': [], 'Completed': [], 'Cancelled': []}
        
        include_status = request.query_params.get('status') == 'true'

        include_total = request.query_params.get('total') == 'true'
        total_amount = 0
        total_count = 0

        include_week = request.query_params.get('week') == 'true'
        weekly_totals = {}

        include_day = request.query_params.get('day') == 'true'
        daily_totals = {}

        include_order_item = request.query_params.get('totalorderitem') == 'true'
        order_item_total = 0

        sorted_queryset = sorted(queryset, key=lambda order: order.created_at)

        for order in sorted_queryset:
            if include_status:
                serializer = OrderSerializer(order)
                order_data = serializer.data

                if order.vendor:
                    vendor_serializer = VendorSerializer(order.vendor)
                    vendor_data = vendor_serializer.data
                    order_data['vendor'] = vendor_data
                
                if order.customer:
                    customer_serializer = CustomerSerializer(order.customer)
                    customer_data = customer_serializer.data
                    order_data['customer'] = customer_data

                status = order_data['status']

                result[status].append(order_data)

            # Include total count in the response if requested
            if include_total and order.status == 'Completed':
                total_amount += order.total_price
                total_count += 1

            if include_week:
                # Calculate weekly totals
                week_number = order.created_at.isocalendar()[1]  # Get ISO week number
                weekly_totals.setdefault(week_number, 0)
                weekly_totals[week_number] += order.total_price

            if include_day and order.status == 'Completed':
                # Calculate daily totals
                order_day_str = order.created_at.strftime('%d %b %y')
                daily_totals.setdefault(order_day_str, 0)
                daily_totals[order_day_str] += order.total_price

            # Include order item quantity if requested
            if include_order_item:
                order_items = OrderItem.objects.filter(order=order)
                total_quantity = sum(item.quantity for item in order_items)
                order_item_total += total_quantity
                
        if include_total:
            result['total_count'] = total_count
            result['total_amount'] = total_amount
        
        if include_week:
            result['weekly_totals'] = weekly_totals
        
        if include_day:
            result['daily_totals'] = daily_totals

        if include_order_item:
            result['order_item_quantity'] = order_item_total

        return Response(result)

class OrderRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrVendor]

    def perform_update(self, serializer):
        user = self.request.user
        if user.role == 'C':
            raise PermissionDenied("Customers are not allowed to update orders.")
        serializer.save()


# class CustomerOrderItemsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         # Assuming you have some way to identify the customer, e.g., through authentication
#         user = request.user  # Replace this with your actual way of getting the customer

#         if user.role == 'C':
#             # Retrieve all OrderItems for the customer
#             order_items = OrderItem.objects.filter(order__customer=user.customer)

#             # Serialize the data
#             serializer = CustomerOrderItemSerializer(order_items, many=True)

#             return Response(serializer.data, status=status.HTTP_200_OK)
        
#         raise PermissionDenied("User does not have the required role for this operation.")
    

class CustomerOrderItemsStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        orders = OrderItem.objects.filter(order__customer=user.customer.id)
        result = {'Expired': [], 'Near Expiry': [], 'Within Shelf Life': []}

        for order in orders:
            serializer = CustomerOrderItemSerializer(order)
            order_data = serializer.data

            status = order_data['product']['status']

            result[status].append(order_data)


        return Response(result)