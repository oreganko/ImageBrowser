from django.http import HttpResponse

from image_browser.models import ImageInstance


def get_domain(request):
    return request.META['HTTP_HOST']


def detail(request, img_id):
    img = ImageInstance.objects.get(pk=img_id)
    img_url = img.image_file.thumbnails.small.url
    return HttpResponse(f'{get_domain(request)}{img_url}')
