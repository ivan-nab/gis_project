import json

from django.contrib.auth.models import Group, User
from django.db.models import Avg
from rest_framework import serializers

from gis_app.models import Location, UserAccount, UserPosition, Vehicle


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'lat', 'lon']


class UserPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPosition
        fields = ['id', 'position', 'fetch_time']


class UserSummarySerializer(serializers.ModelSerializer):
    avg_coords = serializers.SerializerMethodField()
    vehicles = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'email', 'avg_coords', 'vehicles']

    def get_avg_coords(self, obj):
        start_time = self.context.get('start_time')
        end_time = self.context.get('end_time')
        if obj.avg_coords and not (start_time or end_time):
            return json.loads(obj.avg_coords)
        avg_coords = obj.calculate_avg_coords(start_time, end_time)
        return avg_coords

    def get_vehicles(self, obj):
        return json.loads(obj.vehicles or "[]")


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

    def update(self, instance, validated_data):
        vehicle = Vehicle.objects.get(pk=instance.id)
        vehicle.users.add(self.context['request'].user)
        return vehicle
