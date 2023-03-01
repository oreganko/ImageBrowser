from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from image_browser.models import ImageInstance, User

admin.site.register(User, UserAdmin)
admin.site.register(ImageInstance)
