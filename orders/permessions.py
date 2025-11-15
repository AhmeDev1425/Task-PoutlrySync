from rest_framework.permissions import BasePermission
from .models import User

class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.ROLES[0][0]
class IsOperator(BasePermission):
    """
    Custom permission to only allow operator users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.ROLES[1][0]

class IsAdminOrOperator(BasePermission):
    """ both (OR logic) """
    def has_permission(self, request, view):
        return IsAdmin().has_permission(request, view) or \
               IsOperator().has_permission(request, view)
