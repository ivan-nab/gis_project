from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from gis_app.models import Location
from gis_app.serializers import UserSerializer, GroupSerializer, \
                                LocationSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for edit or view users
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for edit or view user groups
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for edit or view locations
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
