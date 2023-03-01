from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from image_browser.models import ImageInstance, TempUrl
from image_browser.permissions import IsOwnerOrAdmin, CanUpload, CanCreateExpiringLink, IsOwnerByUrlImageId
from image_browser.serializers import ImageInstanceSerializer, get_serializer_for_user_plan, TempLinkSerializer, \
    ShowTempLinkSerializer
from image_browser.utils import get_image_name


class ImageInstanceCreation(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, CanUpload]
    queryset = ImageInstance.objects.all()
    serializer_class = ImageInstanceSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        new_context = {'request': request}

        # after upload user has to see links dependent on plan
        view_serializer = get_serializer_for_user_plan(request.user)
        new_data = view_serializer(serializer.save(), context=new_context).data
        return Response(new_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        owner = self.request.user
        temp_name = self.request.data['name']
        img_orig_name = self.request.data['image_file'].name

        # ensure that name length meets the limit if it is taken from image name
        name = temp_name if temp_name else get_image_name(img_orig_name)

        return serializer.save(owner=owner, name=name)


class ImageInstanceDetail(generics.RetrieveAPIView):

    def get_serializer_class(self):
        return get_serializer_for_user_plan(self.request.user)

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = ImageInstance.objects.all()


class ImageInstanceList(generics.ListAPIView):

    def get_serializer_class(self):
        return get_serializer_for_user_plan(self.request.user)

    def get_queryset(self):
        return ImageInstance.objects.filter(owner=self.request.user)

    permission_classes = [permissions.IsAuthenticated]
    queryset = ImageInstance.objects.all()


class TempLinkCreation(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, CanUpload,
                          CanCreateExpiringLink, IsOwnerByUrlImageId]
    serializer_class = TempLinkSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['image_pk'] = kwargs['pk']
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        view_serializer = ShowTempLinkSerializer
        new_context = {'request': request}
        new_data = view_serializer(serializer.save(), context=new_context).data
        return Response(new_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        image: ImageInstance = ImageInstance.objects.get(pk=serializer.validated_data['image_pk'])
        time_seconds = serializer.validated_data['expires_seconds']

        # those parameters are not model attributes, have to be deleted
        del serializer.validated_data['expires_seconds']
        del serializer.validated_data['image_pk']

        date = timezone.now() + timedelta(seconds=int(time_seconds))
        url_hash = image.get_hash()
        binary_image = image.get_binary()

        return serializer.save(url_hash=url_hash, expiration_date=date, image=binary_image)


def temp_link(request, hash):
    url: TempUrl = get_object_or_404(TempUrl, url_hash=hash,
                                     expiration_date__gte=timezone.now()
                                     )
    return HttpResponse({url.image})
