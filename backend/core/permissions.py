"""Custom permissions for API views."""
from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    """Allow read-only requests for authenticated users and staff for mutating."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(request.user and getattr(request.user, "is_staff", False))


class IsStaffOrBotForWrite(BasePermission):
    """Allow staff or authenticated bots to perform write operations."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        user = request.user
        if not user:
            return False

        if getattr(user, "is_staff", False):
            return True

        # BotUser is authenticated but has no is_staff attribute.
        if user.__class__.__name__ == "BotUser" and request.auth:
            return True
        return False
