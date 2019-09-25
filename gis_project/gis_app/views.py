from django.shortcuts import render
from rest_framework import viewsets

from gis_app.serializers import GeoSiteSerializer

from gis_app.models import GeoSite
# Create your views here.


class GeoSiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for access to objects location
    """
    queryset = GeoSite.objects.all()
    serializer_class = GeoSiteSerializer
