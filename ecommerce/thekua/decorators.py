from django.http import HttpResponseForbidden
from functools import wraps
from .models import Role


def admin_or_seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Login required")

        if not request.user.roles.filter(
            role__in=[Role.ADMIN, Role.SELLER],
            active=True
        ).exists():
            return HttpResponseForbidden("Permission denied")

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Login required")

        if not request.user.roles.filter(
            role=Role.ADMIN,
            active=True
        ).exists():
            return HttpResponseForbidden("Admin only")

        return view_func(request, *args, **kwargs)
    return _wrapped_view
