from django.contrib.auth.models import Group, User
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, \
                                        IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

from gis_app.models import Location, UserPosition, Vehicle, UserAccount
from gis_app.serializers import (GroupSerializer, LocationSerializer,
                                 UserPositionSerializer, UserSerializer,
                                 UserSummarySerializer, VehicleSerializer)


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
        vehicle.users.add(self.request.user)
        vehicle.save()
        return Response({
            'status':
            f'vehicle {vehicle.name} attached to user {self.request.user.username}'
        })

    @action(detail=True, methods=['post'])
    def detach_user(self, request, pk=None):
        vehicle = self.get_object()
        vehicle.users.remove(self.request.user)
        vehicle.save()
        return Response({
            'status':
            f'vehicle {vehicle.name} detached from user {self.request.user.username}'
        })
