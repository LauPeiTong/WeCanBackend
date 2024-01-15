from rest_framework import viewsets, permissions
from django.db.models import Sum

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