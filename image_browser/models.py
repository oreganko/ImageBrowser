from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from thumbnails.fields import ImageField


# setting file path to MEDIA_ROOT/user_<user_id>/<filename> for links readability
def user_directory_path(instance, filename):
    return f'user_{instance.owner.username}/{filename}'


class ImageInstance(models.Model):
    image_file = ImageField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
