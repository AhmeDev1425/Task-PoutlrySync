from rest_framework.permissions import BasePermission
from .models import User


class IsAdmin(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN

class IsOperator(BasePermission):
    """
    Custom permission to only allow operator users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.Role.OPERATOR
    
class IsViewer(BasePermission):
    """
    Custom permission to only allow viewer users to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.Role.VIEWER
    
