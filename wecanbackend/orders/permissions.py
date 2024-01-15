from rest_framework import permissions


class IsCustomerOrVendor(permissions.BasePermission):
    """
    Custom permission to allow access to the object only if the user is the customer or vendor of the order.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        print(user.id)
        return obj.customer.id == user.id or obj.vendor.id == user.id