import json
import logging
import os
import uuid

import mz2geohash
import requests
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from gis_app.exceptions import ExternalServiceError
from gis_app.models import (UserPosition, UserPositionExport, Vehicle,
                            VehicleExport)


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
        return render_to_string(self.template, {"objects": list(values)})

    def export_to_file(self, file_name):
        with open(file_name, "w+b") as dest_pdf:
            pisa.CreatePDF(self.export_to_string(), dest=dest_pdf)

    def get_extension(self):
        return ".pdf"


class UserPositionPdfExport(PdfExport):
    def __init__(self):
        self.fields = ['id', 'user__username', 'position__lat', 'position__lon', 'fetch_time']
        self.template = "vehicle_export.html"
        self.queryset = UserPosition.objects.all()


class VehiclePdfExport(PdfExport):
    def __init__(self):
        self.fields = ['id', 'name', 'users__username']
        self.template = "vehicle_export.html"
        self.queryset = Vehicle.objects.all()


class ReportMaker:
    def __init__(self, export_model, exporter):
        self.export_model = export_model
        self.exporter = exporter

    def _get_instance(self, export_id):
        try:
            instance = self.export_model.objects.get(id=export_id)
        except self.export_model.DoesNotExist:
            logging.warning(f"Trying to get non existing {self.export_model.__name__} export '{export_id}'")
        else:
            return instance

    def make_file_path(self):
        return os.path.join(settings.PDF_EXPORTS_DIR, f"{uuid.uuid4()}.{self.exporter.get_extension()}")

    def make_report(self, export_id):
        export_instance = self._get_instance(export_id)
        export_instance.set_status("creating")
        if not export_instance.file_path:
            export_instance.file_path = self.make_file_path()
        self.exporter.export_to_file(file_name=export_instance.file_path)
        export_instance.set_status("done")


class VehicleReportMaker(ReportMaker):
    def __init__(self):
        self.export_model = VehicleExport
        self.exporter = VehiclePdfExport()


class UserPositionReportMaker(ReportMaker):
    def __init__(self):
        self.export_model = UserPositionExport
        self.exporter = UserPositionPdfExport()
