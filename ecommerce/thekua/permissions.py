from rest_framework.permissions import BasePermission,SAFE_METHODS
from thekua.models import Role




class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        # if request.method in SAFE_METHODS: #If request is NOT GET/HEAD/OPTIONS, treat it as a write operation.crud other than get/head/option all are write
        #     return True

        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.roles.filter(
            role__in=self.allowed_roles,
            active=True
        ).exists()


class IsAdmin(HasRole):
    allowed_roles = [Role.ADMIN]


class IsSeller(HasRole):
    allowed_roles = [Role.SELLER]


class IsCustomer(HasRole):
    allowed_roles = [Role.CUSTOMER]


class IsAdminOrSeller(HasRole):
    allowed_roles = [Role.ADMIN, Role.SELLER]


class IsAdminorCustomer(HasRole):
    allowed_roles=[Role.ADMIN,Role.CUSTOMER]


class IsAdminOrSellerOrReadOnly(BasePermission):


    def has_permission(self, request, view):
        # Allow read-only methods for everyone
        if request.method in SAFE_METHODS:
            return True

        # Write permissions → Admin or Seller only
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.roles.filter(
            role__in=[Role.ADMIN, Role.SELLER],
            active=True
        ).exists()

class IsAdminOrCustomerReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.roles.filter(role=Role.CUSTOMER, active=True).exists()
