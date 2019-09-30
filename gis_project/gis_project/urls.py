"""gis_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from gis_app import views

router = routers.DefaultRouter()
router.register(r'api/v1/users', views.UserViewSet)
router.register(r'api/v1/groups', views.GroupViewSet)
router.register(r'api/v1/locations', views.LocationViewSet)
router.register(r'api/v1/userpositions',
                views.UserPositionViewSet,
                basename='UserPosition')
router.register(r'api/v1/usersummary',
                views.UserSummaryViewSet,
                basename='User')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls'))
]

urlpatterns += router.urls
