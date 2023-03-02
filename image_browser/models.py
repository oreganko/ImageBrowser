# Create your models here.
import hashlib
from datetime import datetime
from enum import Enum

from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from rest_framework.exceptions import ValidationError


# setting file path to MEDIA_ROOT/user_<user_id>/<filename> for links readability
def user_directory_path(instance, filename):
    return f'user_{instance.owner.username}/{filename}'


class BuiltInPlans(Enum):
    """ Enum with preexisting builtin plan tiers"""

    BASIC = 'Basic',
    PREMIUM = 'Premium',
    ENTERPRISE = 'Enterprise'


class ThumbnailSize(models.Model):
    """Model of thumbnail sizes
       If it breaks original image proportions - thumbnail is created to bigger of dimensions"""
    height = models.IntegerField()
    width = models.IntegerField()

    def __str__(self):
        return f'{self.height}x{self.width}'


class PlanTier(models.Model):
    """Represents plan tiers"""
    name = models.CharField(max_length=50, null=False, unique=True, primary_key=True)
    thumbnail_sizes = models.ManyToManyField(ThumbnailSize)
    show_original_link = models.BooleanField(null=False)
    create_expiring_link = models.BooleanField(null=False)


class User(AbstractUser):
    """ User class used to authentication"""
    pass


class AppUser(models.Model):
    """ User class that is responsible for plan management """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(PlanTier, on_delete=models.CASCADE)


def validate_file_extension(image_object: InMemoryUploadedFile) -> None:
    """ Validates if image extension is one of .jpg or .png """
    value = image_object.name
    whitelist = ['.jpg', '.jpeg', '.png']
    if not any(value.endswith(extension) for extension in whitelist):
        raise ValidationError('image extension has to be one of .jpg and .png')


class ImageInstance(models.Model):
    """ Model responsible for image management """
    image_file = ThumbnailerImageField(upload_to=user_directory_path,
                                       null=False,
                                       # image has to be .jpg or .png
                                       validators=[validate_file_extension])
    name = models.CharField(max_length=50, default='No name')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_binary(self):
        """ Returns binary of an image."""
        img = Image.open(self.image_file)
        return img.tobytes()

    def get_hash(self):
        """ Returns hash based on ImageInstance properties.
            This method was used instead of __hash__ because this way
            hash can have letters in it."""
        text = self.image_file.name + self.name + self.owner.username + str(datetime.now())
        text_enc = hashlib.sha256(text.encode('utf-8'))
        return text_enc.hexdigest()

    def get_thumbnail_url(self, width: int, height: int):
        """ Returns a URL of thumbnail with given width and height.
            If sizes change image proportions - only bigger value is taken into process
            and the other is adjusted so proportions stays the same as in original file"""
        options = {'size': (width, height), 'crop': False}
        return get_thumbnailer(self.image_file).get_thumbnail(options).url

    def __str__(self):
        return self.name


class TempUrl(models.Model):
    """ Model responsible for expiring links management.
        Keeps binary of an image and link expiration time.
        Hash is used for URL creation. """
    url_hash = models.CharField(blank=False, max_length=100, unique=True)
    expiration_date = models.DateTimeField()
    image = models.BinaryField()
