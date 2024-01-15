# authentication/views.py

from .models import User, Vendor
from .serializers import UserSerializer, VendorSerializer, CustomerSerializer

from django.db.models import Q

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

                    user_instance = vendor_serializer.instance
                    token, created = Token.objects.get_or_create(user=user_instance)
                    return Response({'token': token.key, 'id' : user_instance.id, 'customer_data': vendor_serializer.data}, status=status.HTTP_201_CREATED)
                return Response(vendor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif request.data.get('role') == 'C':
                customer_data = request.data.copy()
                customer_data['latitude'] = latitude
                customer_data['longitude'] = longitude
                customer_serializer = CustomerSerializer(data=customer_data)

                if customer_serializer.is_valid():
                    customer_serializer.save()

                    user_instance = customer_serializer.instance
                    token, created = Token.objects.get_or_create(user=user_instance)
                    return Response({'token': token.key, 'id' : user_instance.id, 'customer_data': customer_serializer.data}, status=status.HTTP_201_CREATED)
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
                return Response({'token': token.key, 'username': user.username, 'role': user.role, 'id' : user.id, 'vendor_data': serializer.data})
            elif user.role == 'C':
                serializer = CustomerSerializer(user.customer)
                return Response({'token': token.key, 'username': user.username, 'role': user.role, 'id' : user.id, 'customer_data': serializer.data})
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


class VendorListView(APIView):
    def get(self, request):
        # Check if the user has a related customer
        customer = getattr(request.user, 'customer', None)

        if customer:
            # If the user has a related customer, use its latitude and longitude
            customer_latitude = customer.latitude
            customer_longitude = customer.longitude
        else:
            # If the user does not have a related customer, set default values or handle accordingly
            customer_latitude = None
            customer_longitude = None

        # Get tags from the request query parameters
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split('-') if '-' in tags else [tags]
            # Using Q objects to perform case-insensitive search in JSONField
            q_objects = [Q(tags__icontains=tag) for tag in tag_list]
            query = Q()

            for q_object in q_objects:
                query |= q_object

            vendors = Vendor.objects.filter(query)
        else:
            vendors =  Vendor.objects.all()

        # Calculate distance for each vendor and include it in the serialized data
        serialized_data = []
        for vendor in vendors:
            distance = None

            # Check if customer's latitude and longitude are available
            if customer_latitude is not None and customer_longitude is not None:
                distance = vendor.distance_to_customer(customer_latitude, customer_longitude)

            vendor_data = VendorSerializer(vendor).data
            vendor_data['distance'] = distance
            vendor_data['latitude'] = vendor.latitude
            vendor_data['longitude'] = vendor.longitude
            vendor_data['tags'] = vendor.tags
            serialized_data.append(vendor_data)

        return Response(serialized_data)