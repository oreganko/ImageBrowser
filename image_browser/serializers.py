from rest_framework import serializers
from abc import ABC, abstractmethod

from image_browser.models import ImageInstance


class ImageInstanceSerializer(serializers.HyperlinkedModelSerializer):
    url_field = serializers.SerializerMethodField()

    class Meta:
        model = ImageInstance
        fields = ['url_field']

    @abstractmethod
    def get_url_field(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file.url
        return request.build_absolute_uri(image_url)


class ImageInstanceSmallThumbnailSerializer(ImageInstanceSerializer):
    def get_url_field(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file['small'].url
        return request.build_absolute_uri(image_url)


class ImageInstanceLargeThumbnailSerializer(ImageInstanceSerializer):
    def get_url_field(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file['large'].url
        return request.build_absolute_uri(image_url)


class ImageInstanceArbitraryThumbnailSerializer(ImageInstanceSerializer):
    def get_url_field(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.get_thumbnail_url(self.context['width'], self.context['height'])
        return request.build_absolute_uri(image_url)