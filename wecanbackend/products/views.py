from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsVendorPermission, IsCustomerPermission
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsVendorPermission | IsCustomerPermission, IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role == 'V':
            serializer.save(vendor=self.request.user)
        else:
            raise PermissionError("Only vendors can create products")

    def get_queryset(self):
        return Product.objects.all()
    
