from rest_framework.permissions import BasePermission,SAFE_METHODS
from thekua.models import Role

# class IsAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.roles.filter(
#             role="admin", active=True
#         ).exists()


# class IsSeller(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.roles.filter(
#             role="seller", active=True
#         ).exists()


# class IsCustomer(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.roles.filter(
#             role="customer", active=True
#         ).exists()
    
# class IsAdminOrSeller(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
#             return (
#                 request.user.is_authenticated
#                 and request.user.roles.filter(
#                     role__in=["admin", "seller"],
#                     active=True
#                 ).exists()
#             )
#         return True


class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS: #If request is NOT GET/HEAD/OPTIONS, treat it as a write operation.crud other than get/head/option all are write
            return True

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