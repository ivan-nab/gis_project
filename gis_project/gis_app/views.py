from django.contrib.auth.models import Group, User
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from gis_app.models import Location, UserPosition, Vehicle, UserVehicle
from gis_app.serializers import (GroupSerializer, LocationSerializer,
                                 UserPositionSerializer, UserSerializer,
                                 UserSummarySerializer, VehicleSerializer,
                                 UserVehicleSerializer)


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
    
    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     serializer = UserSummarySerializer(queryset, many=True)
    #     return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        start_time = parse_datetime(
            self.request.query_params.get('start_time', ''))
        end_time = parse_datetime(self.request.query_params.get(
            'end_time', ''))
        context['start_time'] = start_time
        context['end_time'] = end_time
        return context

    def get_queryset(self):
        qs = User.objects.filter(id=self.request.user.id)
        return qs


class VehicleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for view all vehicles
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def partial_update(self, request, pk=None):
        vehicle = self.get_object()
        serialized = VehicleSerializer(vehicle,
                                       data=request.data,
                                       context={'request': request},
                                       partial=True)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Response(serialized.data)


class UserVehicleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for create or
    delete vehicles of current user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserVehicleSerializer

    def get_queryset(self):
        return UserVehicle.objects.filter(user=self.request.user)
