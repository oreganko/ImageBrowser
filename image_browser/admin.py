from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
from image_browser.models import ImageInstance, User, TempUrl, AppUser, PlanTier, ThumbnailSize


class AppUserInline(admin.StackedInline):
    model = AppUser
    can_delete = False
    verbose_name_plural = 'app users'


class UserAdmin(BaseUserAdmin):
    inlines = (AppUserInline,)


admin.site.register(User, UserAdmin)
admin.site.register(ImageInstance)
admin.site.register(TempUrl)
admin.site.register(PlanTier)
admin.site.register(ThumbnailSize)
