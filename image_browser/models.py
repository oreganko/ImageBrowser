from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField


# setting file path to MEDIA_ROOT/user_<user_id>/<filename> for links readability
from easy_thumbnails.files import get_thumbnailer


def user_directory_path(instance, filename):
    return f'user_{instance.owner.username}/{filename}'


class ImageInstance(models.Model):
    image_file = ThumbnailerImageField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_thumbnail_url(self, width, height):
        options = {'size': (width, height), 'crop': True}
        return get_thumbnailer(self.image_file).get_thumbnail(options).url
