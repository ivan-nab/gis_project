import os
from unittest import mock

from django.template.loader import render_to_string
from rest_framework.test import APITestCase, override_settings

from gis_app.models import Vehicle
from gis_app.services import PdfExport
from gis_app.tasks import create_pdf_report_for_vehicles_task

from .factories import UserFactory, VehicleExportFactory, VehicleFactory


class PdfExportTestCase(APITestCase):
    def setUp(self):
        super(PdfExportTestCase, self).setUp()
        self.user = UserFactory()
        self.vehicles = VehicleFactory.create_batch(3, users=(UserFactory(), ))
        self.fields = ['id', 'name']

    def test_pdf_export_to_string(self):
        qs = Vehicle.objects.all()
        values = qs.values(*self.fields)
        expected_html = render_to_string("vehicle_export.html", {"objects": values})
        exporter = PdfExport(qs, self.fields, "vehicle_export.html")
        html = exporter.export_to_string()
        self.assertEqual(html, expected_html)

    @override_settings(CELERY_BROKER_URL="memory://localhost/")
    @mock.patch('gis_app.signals.create_pdf_report_for_vehicles_task.apply_async')
    def test_vehicle_export(self, create_pdf_report_for_vehicles_task_mock):
        vehicle_export = VehicleExportFactory()
        create_pdf_report_for_vehicles_task_mock.assert_called_with((vehicle_export.id, ), countdown=3)
        create_pdf_report_for_vehicles_task(vehicle_export.id)
        vehicle_export.refresh_from_db()
        self.assertTrue(os.path.exists(vehicle_export.file_path))
        self.assertEqual(vehicle_export.status, "done")

    @override_settings(CELERY_BROKER_URL="memory://localhost/")
    @mock.patch('gis_app.models.VehicleExport.set_status')
    @mock.patch('gis_app.signals.create_vehicle_export_handler')
    def test_change_task_statuses(self, create_vehicle_export_handler_mock, set_status_mock):
        vehicle_export = VehicleExportFactory()
        self.assertEqual(vehicle_export.status, "new")
        create_pdf_report_for_vehicles_task(vehicle_export.id)
        set_status_mock.assert_has_calls([mock.call("creating"), mock.call("done")])
