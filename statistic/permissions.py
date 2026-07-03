from rest_framework.permissions import BasePermission,SAFE_METHODS

class StatistikaPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role.name == "admin"
            and request.method in SAFE_METHODS
        )