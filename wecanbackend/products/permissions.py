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
        return request.user.role == 'V'

    def has_permission(self, request, view):
        # Allow users with role 'V' to create objects
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'V'
    
    def has_object_update_permission(self, request, view, obj):
        # Allow updating only if the user is a vendor and owns the product
        # print(request.user.id)
        # print(obj.vendor.id)
        return request.user.role == 'V' and obj.vendor.id == request.user.id

