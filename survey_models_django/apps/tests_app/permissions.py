from rest_framework.permissions import BasePermission


METHODS = ['POST', 'PUT', 'DELETE']


class StaffOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in METHODS:
            return request.user.is_staff
        return True
