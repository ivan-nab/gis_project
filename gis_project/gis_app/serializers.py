from rest_framework import serializers
from rest_framework_gis.serializers import GeoModelSerializer
from gis_app.models import GeoSite


class GeoSiteSerializer (GeoModelSerializer):

    class Meta:
        model = GeoSite
        fields = ['name', 'location']
