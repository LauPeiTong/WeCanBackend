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
        # override the list method to add the total amount
        response = super().list(request, *args, **kwargs) # call the original list method
        total_amount = Donation.objects.aggregate(total_amount=Sum('amount')) # calculate the total amount of all donations
        response.data['total_amount'] = total_amount['total_amount'] # add the total amount to the response data
        return response # return the response with the paginated data and the total amount
    
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