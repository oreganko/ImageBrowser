from rest_framework import generics

from image_browser.models import ImageInstance
from image_browser.serializers import ImageInstanceSerializer, ImageInstanceSmallThumbnailSerializer, \
    ImageInstanceLargeThumbnailSerializer


class ImageInstanceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSerializer


class ImageInstanceSmallThumbnail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSmallThumbnailSerializer


class ImageInstanceLargeThumbnail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceLargeThumbnailSerializer
