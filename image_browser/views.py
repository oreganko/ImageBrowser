from django.http import HttpResponse

from image_browser.models import ImageInstance


def get_domain(request):
    return request.META['HTTP_HOST']


def thumbnail_height_200(request, img_id):
    img = ImageInstance.objects.get(pk=img_id)
    img_url = img.image_file['small'].url
    return HttpResponse(f'{get_domain(request)}{img_url}')


def thumbnail_height_400(request, img_id):
    img = ImageInstance.objects.get(pk=img_id)
    img_url = img.image_file['large'].url
    return HttpResponse(f'{get_domain(request)}{img_url}')


def thumbnail_get_size(request, img_id):
    img: ImageInstance = ImageInstance.objects.get(pk=img_id)
    img_url = img.get_thumbnail_url(10000, 0)
    return HttpResponse(f'{get_domain(request)}{img_url}')


def detail(request, img_id):
    return thumbnail_get_size(request, img_id)
