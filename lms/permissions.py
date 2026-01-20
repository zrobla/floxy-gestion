from rest_framework import permissions


class IsLmsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in {"OWNER", "ADMIN", "MANAGER"}
        )


class IsEnrollmentOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) in {"OWNER", "ADMIN", "MANAGER"}:
            return True
        owner = getattr(obj, "user", None)
        if owner is None and hasattr(obj, "enrollment"):
            owner = getattr(obj.enrollment, "user", None)
        return owner == user


class IsReadOnlyOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in {"OWNER", "ADMIN", "MANAGER"}
        )
