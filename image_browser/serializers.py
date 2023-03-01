from rest_framework import serializers
from image_browser.models import ImageInstance


class ImageInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageInstance
        fields = ('image_file', 'name')


class BasicPlanImageSerializer(serializers.HyperlinkedModelSerializer):
    small_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageInstance
        fields = ['small_thumbnail_url']

    def get_small_thumbnail_url(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file['small'].url
        return request.build_absolute_uri(image_url)


class PremiumPlanImageSerializer(BasicPlanImageSerializer):
    large_thumbnail_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageInstance
        fields = ['small_thumbnail_url', 'large_thumbnail_url', 'image_url']

    def get_large_thumbnail_url(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file['large'].url
        return request.build_absolute_uri(image_url)

    def get_image_url(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file.url
        return request.build_absolute_uri(image_url)


class EnterprisePlanImageSerializer(PremiumPlanImageSerializer):
    def get_arbitrary_url_field(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.get_thumbnail_url(self.context['width'], self.context['height'])
        return request.build_absolute_uri(image_url)