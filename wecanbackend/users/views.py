# authentication/views.py

from .models import User
from .serializers import UserSerializer, VendorSerializer, CustomerSerializer

from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
import requests


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
                        
            # Check if latitude and longitude are provided
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            # If latitude and longitude are not provided, fetch them from OpenCageData based on the address
            if latitude is None or longitude is None:
                address = request.data.get('address')
                if address:
                    # Replace 'YOUR_OPENCAGE_API_KEY' with your actual OpenCageData API key
                    opencage_api_key = 'ac8dde804c164035951250eca1859dae'
                    opencage_url = f'https://api.opencagedata.com/geocode/v1/json?q={address}&key={opencage_api_key}'

                    response = requests.get(opencage_url)
                    data = response.json()

                    if 'results' in data and len(data['results']) > 0:
                        geometry = data['results'][0]['geometry']
                        latitude = geometry['lat']
                        longitude = geometry['lng']

            if request.data.get('role') == 'V':
                vendor_data = request.data.copy()
                vendor_data['latitude'] = latitude
                vendor_data['longitude'] = longitude
                vendor_serializer = VendorSerializer(data=vendor_data)

                if vendor_serializer.is_valid():
                    vendor_serializer.save()
                    return Response(vendor_serializer.data, status=status.HTTP_201_CREATED)
                return Response(vendor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif request.data.get('role') == 'C':
                customer_data = request.data.copy()
                customer_data['latitude'] = latitude
                customer_data['longitude'] = longitude
                customer_serializer = CustomerSerializer(data=customer_data)

                if customer_serializer.is_valid():
                    customer_serializer.save()
                    return Response(customer_serializer.data, status=status.HTTP_201_CREATED)
                return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            if created:
                token.delete()  # Delete the token if it was already created
                token = Token.objects.create(user=user)

            if user.role == 'V':
                serializer = VendorSerializer(user.vendor)
                return Response({'token': token.key, 'username': user.username, 'role': user.role, 'vendor_data': serializer.data})
            elif user.role == 'C':
                serializer = CustomerSerializer(user.customer)
                return Response({'token': token.key, 'username': user.username, 'role': user.role, 'customer_data': serializer.data})
            else:
                return Response({'token': token.key, 'username': user.username, 'role': user.role})

        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class UserLogoutView(APIView):
    def post(self, request):
        print(request.headers) 
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()

        return Response({'detail': 'Successfully logged out.'})


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
