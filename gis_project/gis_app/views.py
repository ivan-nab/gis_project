from django.core.cache import cache
from django.contrib.auth.models import Group
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

import gis_app.services as services
from gis_app.models import Location, UserAccount, UserPosition, Vehicle
from gis_app.serializers import (GroupSerializer, LocationSerializer, UserPositionSerializer, UserSerializer,
                                 UserSummarySerializer, VehicleSerializer, CoordsStringSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for edit or view users
    """
    queryset = UserAccount.objects.all().order_by('-date_joined')
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
        user = UserAccount.objects.get(id=self.request.user.id)
        return UserPosition.objects.filter(user=user)

    def perform_create(self, serializer):
        user = UserAccount.objects.get(id=self.request.user.id)
        serializer.save(user=user)


class UserSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for view user info
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSummarySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        start_time = parse_datetime(self.request.query_params.get('start_time', ''))
        end_time = parse_datetime(self.request.query_params.get('end_time', ''))
        context['start_time'] = start_time
        context['end_time'] = end_time
        return context

    def get_queryset(self):
        qs = UserAccount.objects.filter(id=self.request.user.id)
        return qs


class VehicleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for view all vehicles
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    @action(detail=True, methods=['post'])
    def attach_user(self, request, pk=None):
        vehicle = self.get_object()
        user = UserAccount.objects.get(id=self.request.user.id)
        vehicle.users.add(user)
        vehicle.save()
        return Response({'status': f'vehicle {vehicle.name} attached to user {user.username}'})

    @action(detail=True, methods=['post'])
    def detach_user(self, request, pk=None):
        vehicle = self.get_object()
        user = UserAccount.objects.get(id=self.request.user.id)
        vehicle.users.remove(user)
        vehicle.save()
        return Response({'status': f'vehicle {vehicle.name} detached from user {self.request.user.username}'})


class DistanceViewSet(viewsets.ViewSet):
    def get_queryset(self):
        return UserPosition.objects.filter(user=self.request.user).latest('fetch_time')

    def list(self, request):
        user_position = self.get_queryset()
        start_coords = (user_position.position.lat, user_position.position.lon)

        end_position_param = request.query_params.get('end')
        coords_serializer = CoordsStringSerializer(data=end_position_param)
        coords_serializer.is_valid(raise_exception=True)

        end_coords = (coords_serializer.data.get('lat'), coords_serializer.data.get('lon'))

        geohash = services.get_hash_for_coords(start_coords, end_coords)

        data = cache.get(geohash)
        if data:
            return Response(data)
        distance = services.get_distance_from_openrouteservice(start_coords, end_coords)
        if distance:
            cache.set(geohash, {"distance": distance})
        return Response({"distance": distance})


