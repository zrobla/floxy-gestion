from rest_framework.permissions import SAFE_METHODS, BasePermission


class TaskPermission(BasePermission):
    message = "Accès refusé pour cette action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if view.action in {"list", "retrieve"}:
            return True
        if view.action == "set_status":
            return True
        return user.role in {"MANAGER", "ADMIN"}

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS or view.action == "retrieve":
            if user.role == "STAFF":
                return obj.assigned_to_id == user.id
            return True
        if view.action == "set_status":
            if user.role == "STAFF":
                return obj.assigned_to_id == user.id
            return user.role in {"MANAGER", "ADMIN"}
        return user.role in {"MANAGER", "ADMIN"}


class ManagerAdminPermission(BasePermission):
    message = "Accès réservé aux gestionnaires."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return user.role in {"OWNER", "MANAGER", "ADMIN"}
        return user.role in {"MANAGER", "ADMIN"}
