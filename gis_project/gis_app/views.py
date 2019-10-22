from django.core.cache import cache
from django.contrib.auth.models import Group, User
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

import gis_app.services as services
from gis_app.models import Location, UserAccount, UserPosition, Vehicle
from gis_app.serializers import (GroupSerializer, LocationSerializer,
                                 UserPositionSerializer, UserSerializer,
                                 UserSummarySerializer, VehicleSerializer,
                                 DistanceSerializer)


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
        return Response({
            'status':
            f'vehicle {vehicle.name} attached to user {user.username}'
        })

    @action(detail=True, methods=['post'])
    def detach_user(self, request, pk=None):
        vehicle = self.get_object()
        user = UserAccount.objects.get(id=self.request.user.id)
        vehicle.users.remove(user)
        vehicle.save()
        return Response({
            'status':
            f'vehicle {vehicle.name} detached from user {self.request.user.username}'
        })


class DistanceViewSet(viewsets.ViewSet):
    def list(self, request):
        user_position = UserPosition.objects.filter(
            user=self.request.user).latest('fetch_time')
        start_position = f"{user_position.position.lat},{user_position.position.lon}"
        end_position = request.query_params.get('end')
        try:
            end_position_lat, end_position_lon = end_position.split(",")
            geohash = services.get_hash_for_coords(
                (user_position.position.lat, user_position.position.lon),
                (float(end_position_lat), float(end_position_lon)))
        except ValueError:
            return Response({"error": "incorrect query parameters"})
        data = cache.get(geohash)
        if not data:
            print("fetching from external api")
            data = services.get_distance_from_openrouteservice(
                start_position, end_position)
            distance = data.get('distance')
            if distance:
                cache.set(geohash, data)
        results = DistanceSerializer(data).data
        return Response(results)
