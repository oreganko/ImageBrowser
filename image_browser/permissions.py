from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins of an object to see it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser


class CanSeeSmallThumbnail(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('image_browser.can_see_small_thumbnail')


class CanSeeLargeThumbnail(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('image_browser.can_see_large_thumbnail')


class CanSeeOriginalImage(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('image_browser.can_see_original_image')
