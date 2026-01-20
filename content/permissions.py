from rest_framework.permissions import BasePermission


class ContentItemPermission(BasePermission):
    message = "Accès refusé pour cette action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if view.action in {"list", "retrieve"}:
            return True
        if view.action in {"submit_for_approval", "publish", "add_metrics"}:
            return user.role in {"OWNER", "MANAGER", "ADMIN"}
        if view.action in {"approve", "reject"}:
            return user.role == "OWNER"
        return user.role in {"OWNER", "MANAGER", "ADMIN"}


class OwnerOnlyPermission(BasePermission):
    message = "Accès réservé au propriétaire."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == "OWNER")
