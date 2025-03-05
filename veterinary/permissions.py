from rest_framework.permissions import BasePermission


class IsVeterinarian(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Veterinarian'


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Owner'
