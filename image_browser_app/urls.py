"""image_browser_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from image_browser import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('add/', views.ImageInstanceCreation.as_view(), name='add'),
    path('<int:pk>/', views.ImageInstanceDetail.as_view(), name='detail'),
    path('images/', views.ImageInstanceList.as_view(), name='list'),
    path('make_temp/<int:pk>/', views.TempLinkCreation.as_view(), name='create_temp_link'),
    re_path(r'^temp/(?P<hash>\w+)/?$', views.temp_link, name='temp_link')

]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)