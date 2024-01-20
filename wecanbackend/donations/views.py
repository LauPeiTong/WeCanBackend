from rest_framework import viewsets, permissions
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status

from .models import Donation
from .serializers import DonationSerializer


# Create your views here.

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all() # get all the donations
    serializer_class = DonationSerializer # use the donation serializer
    permission_classes = [permissions.IsAuthenticated] # allow only authenticated users to create, update, or delete donations

    def list(self, request, *args, **kwargs):
        # Check if 'total' query parameter is provided
        include_totals = request.query_params.get('total') == 'true'

        # Initialize total amounts to None
        round_up_total_amount = points_total_amount = overall_total_amount = None

        if include_totals:
            # Calculate total amount for 'Round-up' donations
            round_up_total_amount = Donation.objects.filter(type='Round-up').aggregate(round_up_total_amount=Sum('amount'))['round_up_total_amount']

            # Calculate total amount for 'Points' donations
            points_total_amount = Donation.objects.filter(type='Points').aggregate(points_total_amount=Sum('amount'))['points_total_amount']

            # Calculate the overall total amount
            overall_total_amount = round_up_total_amount + points_total_amount

        # Add the total amounts to the response data only if include_totals is True
        response = super().list(request, *args, **kwargs)
        if include_totals:
            response.data['round_up_total_amount'] = round_up_total_amount
            response.data['points_total_amount'] = points_total_amount
            response.data['overall_total_amount'] = overall_total_amount

        return response
    
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