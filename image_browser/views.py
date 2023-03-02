from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from image_browser.models import ImageInstance, TempUrl
from image_browser.permissions import IsOwnerOrAdmin, CanCreateExpiringLink, IsOwnerByUrlImageId
from image_browser.serializers import PostImageInstanceSerializer, TempLinkSerializer, \
    ShowTempLinkSerializer, ArbitraryPlanSerializer
from image_browser.utils import cut_image_name


class ImageInstanceCreation(generics.CreateAPIView):
    """ Create ImageInstance - here one can upload their image"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = ImageInstance.objects.all()
    serializer_class = PostImageInstanceSerializer

    def post(self, request, *args, **kwargs):
        # for creation PostImageInstanceSerializer is needed
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        new_context = {'request': request}

        # after upload user has to see links dependent on plan
        view_serializer = ArbitraryPlanSerializer
        new_data = view_serializer(serializer.save(), context=new_context).data
        return Response(new_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        owner = self.request.user
        temp_name = self.request.data['name']
        img_orig_name = self.request.data['image_file'].name

        # ensure that name length meets the limit if it is taken from image name
        name = temp_name if temp_name else cut_image_name(img_orig_name)

        return serializer.save(owner=owner, name=name)


class ImageInstanceDetail(generics.RetrieveAPIView):
    """ View od ImageInstance detail - visible fields are dependent on the user plan"""

    serializer_class = ArbitraryPlanSerializer

    # user has to be authenticated and be owner of given image
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = ImageInstance.objects.all()


class ImageInstanceList(generics.ListAPIView):
    """ View of ImageInstance list - visible fields are dependent on the user plan"""

    serializer_class = ArbitraryPlanSerializer

    def get_queryset(self):
        return ImageInstance.objects.filter(owner=self.request.user)

    permission_classes = [permissions.IsAuthenticated]


class TempLinkCreation(generics.CreateAPIView):
    """ Creation of expiring links. Only image owner can create link of their image."""
    permission_classes = [permissions.IsAuthenticated,
                          CanCreateExpiringLink, IsOwnerByUrlImageId]
    serializer_class = TempLinkSerializer

    def post(self, request, *args, **kwargs):
        # first serializer with fields needed to compute and create temp link
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context['image_pk'] = kwargs['pk']
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)

        # then serializer to show created link is needed
        view_serializer = ShowTempLinkSerializer
        new_context = {'request': request}
        new_data = view_serializer(serializer.save(), context=new_context).data
        return Response(new_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # based on context data, image of which link has to be created is taken
        image: ImageInstance = ImageInstance.objects.get(pk=serializer.context['image_pk'])
        time_seconds = serializer.validated_data['expires_seconds']

        # those parameters are not model attributes, have to be deleted
        del serializer.validated_data['expires_seconds']

        # expiring time is computed
        date = timezone.now() + timedelta(seconds=int(time_seconds))
        url_hash = image.get_hash()
        binary_image = image.get_binary()

        return serializer.save(url_hash=url_hash, expiration_date=date, image=binary_image)


def temp_link(request: Request, hash: str):
    """ View of binary image. Link does not work if it is passed its expiration date """
    url: TempUrl = get_object_or_404(TempUrl, url_hash=hash,
                                     expiration_date__gte=timezone.now()
                                     )
    return HttpResponse({url.image})
