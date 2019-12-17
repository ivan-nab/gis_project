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
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'locations/search', views.LocationsSearchViewSet, base_name="locations-search")
router.register(r'locations', views.LocationViewSet, basename='locations')

router.register(r'userpositions',
                views.UserPositionViewSet,
                basename='user-position')
router.register(r'usersummary',
                views.UserSummaryViewSet,
                basename='user-summary')
router.register(r'vehicles/search', views.VehiclesSearchViewSet, base_name="vehicles-search")
router.register(r'vehicles', views.VehicleViewSet, basename='vehicles')
router.register(r'distance', views.DistanceViewSet, basename='distance')
router.register(r'search', views.AggregateSearchViewSet, basename='search')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/', include(router.urls))
]
