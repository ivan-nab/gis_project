import os
from unittest import mock

from django.template.loader import render_to_string
from rest_framework.test import APITestCase

from gis_app.models import Vehicle
from gis_app.services import PdfExport
from gis_app.business_logic import create_pdf_report_for_vehicle

from .factories import UserFactory, VehicleExportFactory, VehicleFactory


class PdfExportTestCase(APITestCase):
    def setUp(self):
        super(PdfExportTestCase, self).setUp()
        self.user = UserFactory()
        self.vehicles = VehicleFactory.create_batch(3, users=(UserFactory(), ))
        self.fields = ['id', 'name']

    @mock.patch('gis_app.signals.create_pdf_report_for_vehicles_task.apply_async')
    def test_pdf_export(self, mock_create_pdf_report_task):
        qs = Vehicle.objects.all()
        values = qs.values(*self.fields)
        expected_html = render_to_string("vehicle_export.html", {"objects": values})
        exporter = PdfExport(qs, self.fields, "vehicle_export.html")
        html = exporter.export_to_string()
        self.assertEqual(html, expected_html)
        vehicle_export = VehicleExportFactory()
        mock_create_pdf_report_task.assert_called_once()
        create_pdf_report_for_vehicle(vehicle_export.id)
        self.assertTrue(os.path.exists(vehicle_export.file_path))
        vehicle_export.refresh_from_db()
        self.assertEqual(vehicle_export.status, "done")
