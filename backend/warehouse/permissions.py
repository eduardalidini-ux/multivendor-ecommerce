from rest_framework.permissions import BasePermission


class IsCourier(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, "courier_profile", None)
        return bool(profile and getattr(profile, "is_active", False))


class IsWarehouseManager(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, "warehouse_manager_profile", None)
        return bool(profile and getattr(profile, "is_active", False))
