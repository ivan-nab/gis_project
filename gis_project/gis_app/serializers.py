from django.db.models import Avg
from django.contrib.auth.models import User, Group
from rest_framework import serializers

from gis_app.models import Location, UserPosition


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
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

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avg_coords']

    def get_avg_coords(self, obj):
        avg_coords = obj.userposition_set.values(
            'position__lon',
            'position__lat').aggregate(lon=Avg('position__lon'),
                                       lat=Avg('position__lat'))

        return avg_coords
