from rest_framework import permissions

class IsVendorPermission(permissions.BasePermission):
    """
    Custom permission to only allow vendors to edit their own products.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the vendor of the product
        return obj.vendor == request.user and request.user.role == 'V'

    def has_permission(self, request, view):
        # Allow users with role 'V' to create objects
        return request.user.role == 'V'
    

class IsCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user has the role 'C' (Customer)
        return request.user.role == 'C'
