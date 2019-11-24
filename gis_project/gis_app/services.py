import json

import mz2geohash
import requests
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from gis_app.exceptions import ExternalServiceError


def get_distance_from_openrouteservice(start, end):
    api_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    params = {
        "api_key": settings.OPENROUTESERVICE_API_KEY,
        "start": f"{start[0]},{start[1]}",
        "end": f"{end[0]},{end[1]}"
    }
    response = requests.get(api_url, params=params)
    obj = json.loads(response.content)
    try:
        distance = obj['features'][0]['properties']['summary']['distance']
    except KeyError:
        raise ExternalServiceError("Error fetching data from openrouteservice API")
    return distance


def get_hash_for_coords(start, end):
    geo_hash = f"{mz2geohash.encode(start)}-{mz2geohash.encode(end)}"
    return geo_hash


class PdfExport:
    def __init__(self, queryset, fields, template):
        self.fields = fields
        self.template = template
        self.queryset = queryset

    def export_to_string(self):
        values = self.queryset.values(*self.fields)
        return render_to_string(self.template, {"objects": values})

    def export_to_pdf(self, file_name):
        with open(file_name, "w+b") as dest_pdf:
            pisa.CreatePDF(self.export_to_string(), dest=dest_pdf)
