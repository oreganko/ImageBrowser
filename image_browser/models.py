# Create your models here.
import hashlib
from datetime import datetime

from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer


# setting file path to MEDIA_ROOT/user_<user_id>/<filename> for links readability
def user_directory_path(instance, filename):
    return f'user_{instance.owner.username}/{filename}'


class User(AbstractUser):

    class Meta:
        permissions = (
            ('has_basic_plan', 'Have basic plan'),
            ('has_premium_plan', 'Have premium plan'),
            ('has_enterprise_plan', 'Have enterprise plan'),
            ('can_upload', 'Can upload an image'),
            ('can_create_expiring_link', 'Can create expiring link'),
        )


def validate_file_extension(obj):
    value = obj.name
    whitelist = ['.jpg', '.jpeg', '.png']
    if not any(value.endswith(extension) for extension in whitelist):
        raise ValidationError('image extension has to be one of .jpg and .png')


class ImageInstance(models.Model):
    image_file = ThumbnailerImageField(upload_to=user_directory_path,
                                       null=False,
                                       # image has to be .jpg or .png
                                       validators=[validate_file_extension])
    name = models.CharField(max_length=50, default='No name')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_thumbnail_url(self, width, height):
        options = {'size': (width, height), 'crop': True}
        return get_thumbnailer(self.image_file).get_thumbnail(options).url

    def get_hash(self):
        text = self.image_file.name + self.name + self.owner.username + str(datetime.now())
        text_enc = hashlib.sha256(text.encode('utf-8'))
        return text_enc.hexdigest()

    def __str__(self):
        return self.name

    def get_binary(self):
        img = Image.open(self.image_file)
        return img.tobytes()


class TempUrl(models.Model):
    url_hash = models.CharField(blank=False, max_length=100, unique=True)
    expiration_date = models.DateTimeField()
    image = models.BinaryField()



