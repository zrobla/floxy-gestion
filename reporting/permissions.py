from rest_framework.permissions import BasePermission


class OwnerAdminPermission(BasePermission):
    message = "Accès réservé au propriétaire."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in {"OWNER", "ADMIN"})
