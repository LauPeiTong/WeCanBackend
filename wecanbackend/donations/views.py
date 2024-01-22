from rest_framework import viewsets, permissions
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


from .models import Donation
from .serializers import DonationSerializer
from users.serializers import CustomerSerializer
from users.models import Customer

# Create your views here.

class DonationPagination(PageNumberPagination):
    page_size = 10  # Number of donations to be displayed per page
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Maximum number of donations that can be requested per page

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DonationPagination  # Use the custom pagination class

    def list(self, request, *args, **kwargs):
        include_totals = request.query_params.get('total') == 'true'
        round_up_total_amount = points_total_amount = overall_total_amount = None

        if include_totals:
            round_up_total_amount = Donation.objects.filter(type='Round-up').aggregate(round_up_total_amount=Sum('amount'))['round_up_total_amount']
            points_total_amount = Donation.objects.filter(type='Points').aggregate(points_total_amount=Sum('amount'))['points_total_amount']
            overall_total_amount = round_up_total_amount + points_total_amount
        
        include_day = request.query_params.get('day') == 'true'
        daily_totals = {}

        # Call super().list to get the default paginated response
        response = super().list(request, *args, **kwargs)

        # Convert the list to a dictionary
        data_dict = {'donations': response.data}

        if include_totals:
            data_dict['round_up_total_amount'] = round_up_total_amount
            data_dict['points_total_amount'] = points_total_amount
            data_dict['overall_total_amount'] = overall_total_amount

        if include_day:
            donations = Donation.objects.all()
            sorted_donations = sorted(donations, key=lambda donation: donation.created_at)

            if sorted_donations:
                # Manually serialize the customer field
                for donation_data in sorted_donations:
                    # Calculate daily totals
                    donation_day_str = donation_data.created_at.strftime('%d %b %y')
                    daily_totals.setdefault(donation_day_str, 0)
                    daily_totals[donation_day_str] += donation_data.amount
            
            data_dict['daily_totals'] = dict(daily_totals)
            return Response(data_dict)
            
        if data_dict['donations']['results']:
            # Manually serialize the customer field
            for donation_data in data_dict['donations']['results']:
                customer_id = donation_data['customer']
                customer = Customer.objects.get(id=customer_id)
                customer_data = CustomerSerializer(customer).data
                donation_data['customer'] = customer_data

        # Return the response with the modified data
        return Response(data_dict)
    
    def create(self, request, *args, **kwargs):
        # Assuming you have a Customer model with a points field
        customer = request.user.customer  # Adjust this based on your authentication setup

        donated_points = request.data.get('points', 0)

        # Check if the customer has enough points to donate
        if customer.points >= donated_points:
            # Deduct the points from the customer
            customer.points -= donated_points
            customer.save()

            # Continue with the donation creation
            return super().create(request, *args, **kwargs)
        else:
            # Return a response indicating insufficient points
            return Response({'error': 'Insufficient points for donation'}, status=status.HTTP_400_BAD_REQUEST)