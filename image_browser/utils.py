from django.urls import reverse
from rest_framework.request import Request

from image_browser.models import User, PlanTier, AppUser, ImageInstance


def cut_image_name(name: str) -> str:
    """Cuts name of file if it is too long.
        :return string in format ...name_ending no longer than 50 characters"""
    return name if len(name) <= 50 else '...' + name[len(name) - 47:]


def get_plan_by_user(user: User) -> PlanTier:
    """ Gets user plan for authenticated user """
    if user.is_staff:
        return PlanTier.objects.get(name='Enterprise')
    return AppUser.objects.get(user=user).plan


def create_expiring_link(image_instance: ImageInstance, request: Request) -> str:
    """ Creates expiring link for given ImageInstance
        based on host given in request"""
    return request.build_absolute_uri(reverse('create_temp_link',
                                              kwargs={'pk': image_instance.id}))
