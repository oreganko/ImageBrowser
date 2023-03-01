from rest_framework import generics, permissions, serializers

from image_browser.models import ImageInstance
from image_browser.permissions import IsOwnerOrAdmin, CanSeeSmallThumbnail, CanSeeLargeThumbnail, CanSeeOriginalImage, \
    CanUpload
from image_browser.serializers import ImageInstanceSerializer, ImageInstanceSmallThumbnailSerializer, \
    ImageInstanceLargeThumbnailSerializer, ImageInstanceURLSerializer
from image_browser.utils import get_image_name


class ImageInstanceCreation(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanUpload]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        owner = self.request.user
        temp_name = self.request.data['name']
        img_orig_name = self.request.data['image_file'].name
        name = temp_name if temp_name else get_image_name(img_orig_name)
        if img_orig_name.endswith('.jpg') or img_orig_name.endswith('.png'):
            return serializer.save(owner=owner, name=name)
        else:
            raise serializers.ValidationError({'detail': 'image extension has to be one of .jpg and .png'})


class ImageInstanceDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeOriginalImage]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceURLSerializer


class ImageInstanceSmallThumbnail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeSmallThumbnail]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSmallThumbnailSerializer


class ImageInstanceLargeThumbnail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeLargeThumbnail]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceLargeThumbnailSerializer
