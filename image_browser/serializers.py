from django.urls import reverse
from rest_framework import serializers
from image_browser.models import ImageInstance, User, TempUrl


def get_serializer_for_user_plan(user: User):
    if user.is_staff:
        return EnterprisePlanImageSerializer
    if user.has_perm('image_browser.has_basic_plan'):
        return BasicPlanImageSerializer
    elif user.has_perm('image_browser.has_premium_plan'):
        return PremiumPlanImageSerializer
    elif user.has_perm('image_browser.has_enterprise_plan'):
        return EnterprisePlanImageSerializer
    else:
        raise PermissionError('This user has no permission to see image')


class ImageInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageInstance
        fields = ('image_file', 'name')


class BasicPlanImageSerializer(serializers.HyperlinkedModelSerializer):
    small_thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageInstance
        fields = ['name', 'small_thumbnail_url']

    def get_small_thumbnail_url(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file['small'].url
        return request.build_absolute_uri(image_url)


class PremiumPlanImageSerializer(BasicPlanImageSerializer):
    large_thumbnail_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageInstance
        fields = ['name', 'small_thumbnail_url', 'large_thumbnail_url', 'image_url']

    def get_large_thumbnail_url(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file['large'].url
        return request.build_absolute_uri(image_url)

    def get_image_url(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.image_file.url
        return request.build_absolute_uri(image_url)


class EnterprisePlanImageSerializer(PremiumPlanImageSerializer):
    create_expiring_link = serializers.SerializerMethodField()

    class Meta:
        model = ImageInstance
        fields = ['name', 'small_thumbnail_url', 'large_thumbnail_url',
                  'image_url', 'create_expiring_link']

    def get_create_expiring_link(self, image_instance: ImageInstance):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('create_temp_link',
                                                  kwargs={'pk': image_instance.id}))

    def get_arbitrary_url_field(self, image_instance: ImageInstance):
        request = self.context.get('request')
        image_url = image_instance.get_thumbnail_url(self.context['width'], self.context['height'])
        return request.build_absolute_uri(image_url)


class TempLinkSerializer(serializers.HyperlinkedModelSerializer):
    expires_seconds = serializers.IntegerField()

    def validate_expires_seconds(self, time_seconds):
        if not 300 <= time_seconds <= 30000:
            raise serializers.ValidationError('Seconds must be value between 300 and 30000')
        return time_seconds

    class Meta:
        model = TempUrl
        fields = ['expires_seconds']


class ShowTempLinkSerializer(serializers.HyperlinkedModelSerializer):
    expiring_link_url = serializers.SerializerMethodField()

    class Meta:
        model = TempUrl
        fields = ['url_hash', 'expiration_date', 'expiring_link_url']

    def get_expiring_link_url(self, temp_url: TempUrl):
        request = self.context.get('request')
        image_url = temp_url.url_hash
        return f'http://{request.get_host()}/temp/{image_url}'
