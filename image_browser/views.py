from rest_framework import generics, permissions, status
from rest_framework.response import Response

from image_browser.models import ImageInstance
from image_browser.permissions import IsOwnerOrAdmin, CanSeeSmallThumbnail, CanSeeLargeThumbnail, CanSeeOriginalImage, \
    CanUpload
from image_browser.serializers import ImageInstanceSerializer, BasicPlanImageSerializer, PremiumPlanImageSerializer, \
    EnterprisePlanImageSerializer
from image_browser.utils import get_image_name


class ImageInstanceCreation(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanUpload]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSerializer

    def post(self, request, *args, **kwargs):
        serializer = ImageInstanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        new_context = {'request': request}
        new_data = PremiumPlanImageSerializer(serializer.save(), context=new_context).data
        return Response(new_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        owner = self.request.user
        temp_name = self.request.data['name']
        img_orig_name = self.request.data['image_file'].name

        # ensure that name length meets the limit if it is taken from image name
        name = temp_name if temp_name else get_image_name(img_orig_name)

        return serializer.save(owner=owner, name=name)


# class ImageInstanceDetail(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeOriginalImage]
#     queryset = ImageInstance.objects.all()
#     serializer_class = ImageInstanceURLSerializer
#
#
# class ImageInstanceSmallThumbnail(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeSmallThumbnail]
#     queryset = ImageInstance.objects.all()
#     serializer_class = ImageInstanceSmallThumbnailSerializer
#
#
# class ImageInstanceLargeThumbnail(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, CanSeeLargeThumbnail]
#     queryset = ImageInstance.objects.all()
#     serializer_class = ImageInstanceLargeThumbnailSerializer
