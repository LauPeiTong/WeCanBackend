from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsVendorPermission
from rest_framework.decorators import action
from rest_framework.response import Response
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count

from .models import Product
from .serializers import ProductSerializer
from users.serializers import VendorSerializer
from users.models import Vendor

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendorPermission]

    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs['pk']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        serialized_product = ProductSerializer(product).data
        return Response(serialized_product)

    def perform_create(self, serializer):
        if self.request.user.role == 'V':
            serializer.save(vendor=self.request.user.vendor)
        else:
            raise PermissionError("Only vendors can create products")
    
    def perform_update(self, serializer):
        obj = self.get_object()
        permission = IsVendorPermission()

        if not permission.has_object_update_permission(self.request, self, obj):
            raise PermissionError("You do not have permission to update this product.")

        serializer.save()
        

    def perform_destroy(self, instance):
        # Check if the user has permission to delete the object
        permission = IsVendorPermission()

        if not permission.has_object_update_permission(self.request, self, instance):
            raise PermissionError("You do not have permission to delete this product.")

        instance.delete()

    def get_queryset(self):
        recommended = self.request.query_params.get('recommended')

        if recommended:
            # Add your logic for fetching recommended products
            recommended_products = (
                Product.objects
                .filter(orderitem__order__isnull=False)  # Filter products with at least one order
                .annotate(num_orders=Count('orderitem__order', distinct=True))
                .order_by('-num_orders')  # Order by the number of orders in descending order
                .filter(num_orders__gt=0)[:20]  # Get the top 20 recommended products
            )
            return recommended_products
            
        return Product.objects.all()
    
    
class VendorProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendorPermission]

    def get_distance(self, request, vendor):
        customer = getattr(request.user, 'customer', None)

        if customer:
            customer_latitude = customer.latitude
            customer_longitude = customer.longitude
            if customer_latitude is not None and customer_longitude is not None:
                distance = vendor.distance_to_customer(customer_latitude, customer_longitude)

            return distance
        else:
            # If the user does not have a related customer, set default values or handle accordingly
            return None

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']
        status_values = ['Within Shelf Life', 'Near Expiry']
        
        # Annotate the products with the count for each category
        annotated_products = Product.objects.filter(vendor__id=vendor_id, status__in=status_values).values('category').annotate(count=Count('category'))

        # Organize products by category using defaultdict
        products_by_category = defaultdict(list)

        for product in annotated_products:
            category = product['category']
            count = product['count']
            products_by_category[category].extend(
            Product.objects.filter(
                    vendor__id=vendor_id,
                    category=category,
                    status__in=status_values
                )[:count]
            )

        # Serialize vendor data
        vendor = Vendor.objects.get(id=vendor_id)
        vendor_data = VendorSerializer(vendor).data
        vendor_data['distance'] = self.get_distance(self.request, vendor)

        # Convert to the desired structure and serialize the products
        organized_products = []
        for category, products in products_by_category.items():
            serialized_products = ProductSerializer(products, many=True).data
            organized_products.append({'category': category, 'products': serialized_products})

        return {'vendor': vendor_data, 'products_data': organized_products}

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset)


# class ProductsByCategoryView(APIView):
#     def get(self, request, *args, **kwargs):
#         # Fetch all products from the database
#         all_products = Product.objects.all()

#         # Organize products by category using defaultdict
#         products_by_category = defaultdict(list)
#         for product in all_products:
#             products_by_category[product.category].append(product)

#         # Convert to the desired structure and serialize the products
#         organized_products = []
#         for category, products in products_by_category.items():
#             serialized_products = ProductSerializer(products, many=True).data
#             organized_products.append({'category': category, 'products': serialized_products})

#         return Response({'organized_products': organized_products}, status=status.HTTP_200_OK)