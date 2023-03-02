from django.urls import reverse
from rest_framework import serializers

from image_browser.models import ImageInstance, TempUrl, PlanTier
from image_browser.utils import get_plan_by_user, create_expiring_link


class ArbitraryPlanSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for any type of plan created by admin on admin site. """

    def get_create_expiring_link(self, image_instance: ImageInstance) -> str:
        """ Method for dispatching 'create_expiring_link' serializer field.
            It keeps link for expiring link creation. """
        request = self.context.get('request')
        return create_expiring_link(image_instance, request)

    def get_image_url(self, image_instance: ImageInstance) -> str:
        """ Method to get original image absolute URL """
        request = self.context.get('request')
        image_url = image_instance.image_file.url
        return request.build_absolute_uri(image_url)

    def get_arbitrary_url_field(self, image_instance: ImageInstance, height: int, width: int) -> str:
        """ Method to get absolute  URL of thumbnail with size given in arguments """
        request = self.context.get('request')
        image_url = image_instance.get_thumbnail_url(width, height)
        return request.build_absolute_uri(image_url)

    class Meta:
        model = ImageInstance
        fields = ('name',)

    def to_representation(self, instance: ImageInstance):
        """ Overriding method to create representation based on user plan.
            Plan is taken based on user creating a request.
            In this method fields for representation are added if they should be
            based on thumbnail sizes in the plan."""
        data = super().to_representation(instance)
        user = self.context.get('request').user
        plan: PlanTier = get_plan_by_user(user)
        if plan:
            if plan.create_expiring_link:
                data['create_expiring_link'] = self.get_create_expiring_link(instance)
            if plan.show_original_link:
                data['image_url'] = self.get_image_url(instance)
            thumb_sizes = plan.thumbnail_sizes.all()
            for thumbnail_size in thumb_sizes:
                data[f'thumbnail_{thumbnail_size}_url'] = self.get_arbitrary_url_field(instance, thumbnail_size.height,
                                                                                       thumbnail_size.width)
        return data


class PostImageInstanceSerializer(serializers.ModelSerializer):
    """ Serializer with only information needed to create an image instance. """

    class Meta:
        model = ImageInstance
        fields = ('image_file', 'name')


class TempLinkSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for expiring link creation. """

    # based on number of seconds given by user, time of expiration is counted
    expires_seconds = serializers.IntegerField()

    # method for expiration seconds validation
    def validate_expires_seconds(self, time_seconds: int) -> int:
        if not 300 <= time_seconds <= 30000:
            raise serializers.ValidationError('Seconds must be value between 300 and 30000.')
        return time_seconds

    class Meta:
        model = TempUrl
        fields = ['expires_seconds']


class ShowTempLinkSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for presenting expiring link after creation. """
    expiring_link_url = serializers.SerializerMethodField()

    class Meta:
        model = TempUrl
        fields = ['url_hash', 'expiration_date', 'expiring_link_url']

    def get_expiring_link_url(self, temp_url: TempUrl) -> str:
        """ Creates expiring link based on hash"""
        request = self.context.get('request')
        image_url = temp_url.url_hash
        uri = reverse('temp_link', kwargs={'hash': image_url})
        return f'http://{request.get_host()}{uri}'
