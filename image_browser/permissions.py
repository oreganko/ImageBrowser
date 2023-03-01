from rest_framework import permissions

from image_browser.models import ImageInstance


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins of an object to see it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser


class IsOwnerByUrlImageId(permissions.BasePermission):
    def has_permission(self, request, view):
        image = ImageInstance.objects.get(id=view.kwargs.get('pk', None))
        return request.user == image.owner or request.user.is_superuser


class CanUpload(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('image_browser.can_upload')


class CanCreateExpiringLink(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('image_browser.can_create_expiring_link')
