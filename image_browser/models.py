# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField

from easy_thumbnails.files import get_thumbnailer


# setting file path to MEDIA_ROOT/user_<user_id>/<filename> for links readability
def user_directory_path(instance, filename):
    return f'user_{instance.owner.username}/{filename}'


class User(AbstractUser):

    class Meta:
        permissions = (
            ('can_see_small_thumbnail', 'Can get URL with small thumbnail'),
            ('can_see_large_thumbnail', 'Can get URL with large thumbnail'),
            ('can_see_original_image', 'Can get URL with original image'),
        )


class ImageInstance(models.Model):
    image_file = ThumbnailerImageField(upload_to=user_directory_path)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_thumbnail_url(self, width, height):
        options = {'size': (width, height), 'crop': True}
        return get_thumbnailer(self.image_file).get_thumbnail(options).url
