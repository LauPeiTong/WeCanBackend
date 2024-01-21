# authentication/views.py

from .models import User, Vendor, Customer
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
from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count

import requests


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer)
                        
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
        
            else:
                serializer.save()
                user_instance = serializer.instance
                token, created = Token.objects.get_or_create(user=user_instance)
                return Response({'token': token.key, 'id' : user_instance.id, 'admin_data': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
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
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class UserLogoutView(APIView):
    def post(self, request):
        print(request.headers) 
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()

        return Response({'detail': 'Successfully logged out.'})


class UserPagination(PageNumberPagination):
    page_size = 10  # Number of donations to be displayed per page
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Maximum number of donations that can be requested per page
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination


    def get_serializer_class(self):
        user = self.request.user

        # Choose the appropriate serializer based on the user's role
        if user.role == 'A':
            return UserSerializer
        elif user.role == 'C':
            return CustomerSerializer
        else:
            return VendorSerializer
        
    def get_vendor_summary(self):
        # Get the top 3 vendors with the highest amount of sales
        top_vendors = Vendor.objects.annotate(total_sales=Sum('orders__total_price')).order_by('-total_sales')[:3]

        # Get the number of vendors based on city
        vendors_by_city = Vendor.objects.values('city').annotate(num_vendors=Count('id'))

        # Get the top 3 cities with the highest number of sales
        top_cities = Vendor.objects.values('city').annotate(total_sales=Sum('orders__total_price')).order_by('-total_sales')[:3]

        return {
            'top_vendors': VendorSerializer(top_vendors, many=True).data,
            'vendors_by_city': vendors_by_city,
            'top_cities': top_cities
        }
    
    def get_customer_summary(self):
         total_customers = Customer.objects.count()

         return {
            'total_customers': total_customers
        }

    def list(self, request, *args, **kwargs):
        user = self.request.user

        include_vendor_summary = request.query_params.get('vendorsummary') == 'true'
        include_customer_summary = request.query_params.get('customersummary') == 'true'
        include_vendor = request.query_params.get('vendors') == 'true'
        include_customer = request.query_params.get('customers') == 'true'

        if include_vendor_summary:
            summary_data = self.get_vendor_summary()
            return Response(summary_data)
        
        if include_customer_summary:
            summary_data = self.get_customer_summary()
            return Response(summary_data)
        
        if include_vendor:
            vendors = Vendor.objects.all()

            vendor_serializer = VendorSerializer(vendors, many=True)

            data_dict = {
                'vendors': vendor_serializer.data
            }

            return Response(data_dict)
        
        if include_customer:
            customers = Customer.objects.all()

            customer_serializer = CustomerSerializer(customers, many=True)

            data_dict = {
                'vendors': vendor_serializer.data
            }

            return Response(data_dict)
        
        else:
            # Call super().list to get the default paginated response
            response = super().list(request, *args, **kwargs)

            # Convert the list to a dictionary
            data_dict = {'users': response.data}

            # Return the response with the modified data
            return Response(data_dict)

    def get_queryset(self):
        user = self.request.user

        # If user role is 'A' (admin), return all users
        if user.role == 'A':
            return User.objects.all()
        elif user.role == 'C':
            return Customer.objects.filter(id=user.customer.id)
        else:
            return Vendor.objects.filter(id=user.vendor.id)

    def perform_create(self, serializer):
        user = self.request.user

        # If user role is not 'A', set the user to themselves
        if user.role != 'A':
            serializer.save(user=user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user

        # If user role is not 'A', ensure they can only update their own details
        if user.role != 'A':
            serializer.save(user=user)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        # If user role is not 'A', ensure they can only delete their own account
        if user.role != 'A' and instance.id == user.id:
            instance.delete()
        elif user.role == 'A':
            instance.delete()
        else:
            # User without 'A' role trying to delete another user's account
            raise PermissionDenied("You do not have permission to delete this user.")


# For customer to see the vendor list
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
        type = request.query_params.get('type', None)
        category = self.request.query_params.get('category')

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

        if category:
            vendors = vendors.filter(category=category)
    
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

            if type == 'near':
                if distance and distance <= 5:
                    serialized_data.append(vendor_data)
            else:
                serialized_data.append(vendor_data)
        
        # Sort the serialized data by distance in ascending order
        sorted_data = sorted(serialized_data, key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))

        return Response(sorted_data)

