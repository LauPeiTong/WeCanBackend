from rest_framework import viewsets, permissions
from .models import Donation
from .serializers import DonationSerializer

# Create your views here.

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all() # get all the donations
    serializer_class = DonationSerializer # use the donation serializer
    permission_classes = [permissions.IsAuthenticated] # allow only authenticated users to create, update, or delete donations
