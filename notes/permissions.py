import os
import secrets

from rest_framework.permissions import BasePermission


class IsAdminApiKey(BasePermission):
    """Grants access only when the 'X-Admin-Key' header matches ADMIN_API_KEY."""

    def has_permission(self, request, view):
        admin_key = os.getenv('ADMIN_API_KEY', '')
        provided = request.META.get('HTTP_X_ADMIN_KEY', '')
        if not admin_key or not provided:
            return False
        return secrets.compare_digest(provided, admin_key)
