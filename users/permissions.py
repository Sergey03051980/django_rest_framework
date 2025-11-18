from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Доступ только владельцу объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsModerator(permissions.BasePermission):
    """Доступ только модераторам"""

    def has_permission(self, request, view):
        return request.user.is_staff


class IsNotModerator(permissions.BasePermission):
    """Запрет модераторам (для создания контента)"""

    def has_permission(self, request, view):
        return not request.user.is_staff

