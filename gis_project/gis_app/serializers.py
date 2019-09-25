from rest_framework import serializers

from gis_app.models import GeoSite


class GeoSiteSerializer (serializers.HyperlinkedModelSerializer):

    class Meta:
        model = GeoSite
        fields = ['name', 'location']
