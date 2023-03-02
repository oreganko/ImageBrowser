from rest_framework import permissions

from image_browser.models import ImageInstance
from image_browser.utils import get_plan_by_user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins of an object to see it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser


class IsOwnerByUrlImageId(permissions.BasePermission):
    """ Custom permission to only allow owners or admins of an object
        given in URL to see it. """

    def has_permission(self, request, view):
        image = ImageInstance.objects.get(id=view.kwargs.get('pk', None))
        return request.user == image.owner or request.user.is_superuser


class CanCreateExpiringLink(permissions.BasePermission):
    """ Custom permission to only allow users that have expiration link creation
        in their plans """
    def has_permission(self, request, view):
        user = request.user
        plan = get_plan_by_user(user)
        return plan.create_expiring_link
