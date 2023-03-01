from rest_framework import generics, permissions

from image_browser.models import ImageInstance
from image_browser.permissions import IsOwnerOrAdmin, CanSeeSmallThumbnail, CanSeeLargeThumbnail, CanSeeOriginalImage
from image_browser.serializers import ImageInstanceSerializer, ImageInstanceSmallThumbnailSerializer, \
    ImageInstanceLargeThumbnailSerializer


class ImageInstanceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeOriginalImage]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSerializer


class ImageInstanceSmallThumbnail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeSmallThumbnail]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSmallThumbnailSerializer


class ImageInstanceLargeThumbnail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeLargeThumbnail]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceLargeThumbnailSerializer
