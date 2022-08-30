from rest_framework import permissions


class IsAdminReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return bool(request.user and request.user.is_staff)


class FullDjangoModelPermission(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class CustomerHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perms('store.view_history')
