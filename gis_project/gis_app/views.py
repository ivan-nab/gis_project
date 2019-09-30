from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from gis_app.models import Location, UserPosition
from gis_app.serializers import UserSerializer, GroupSerializer, \
                                LocationSerializer, UserPositionSerializer, \
                                UserSummarySerializer


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


class UserPositionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for edit or view authenticated user position
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserPositionSerializer

    def get_queryset(self):
        return UserPosition.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for view user info  
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSummarySerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
