from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsVendorPermission
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendorPermission]

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
        return Product.objects.all()
    
    
class VendorProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendorPermission]

    def get_queryset(self):
        vendor_id = self.kwargs['vendor_id']  # Assuming 'vendor_id' is the parameter in the URL
        return Product.objects.filter(vendor__id=vendor_id)