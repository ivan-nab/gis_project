import os
from unittest import mock

from django.template.loader import render_to_string
from rest_framework.test import APITestCase, override_settings

from gis_app.models import UserPosition, Vehicle
from gis_app.services import PdfExport
from gis_app.tasks import (create_pdf_report_for_user_position_task, create_pdf_report_for_vehicles_task)

from .factories import (UserFactory, UserPositionExportFactory, UserPositionFactory, VehicleExportFactory,
                        VehicleFactory)


class PdfExportVehiclesTestCase(APITestCase):
    def setUp(self):
        super(PdfExportVehiclesTestCase, self).setUp()
        self.user = UserFactory()
        self.vehicles = VehicleFactory.create_batch(3, users=(UserFactory(), ))
        self.fields = ['id', 'name', 'users__username']
        self.qs = Vehicle.objects.all()
        self.expected_values = {"objects": list(self.qs.values(*self.fields))}
        self.expected_html = render_to_string("vehicle_export.html", self.expected_values)

    def test_pdf_export_to_string(self):
        exporter = PdfExport(self.qs, self.fields, "vehicle_export.html")
        html = exporter.export_to_string()
        self.assertEqual(html, self.expected_html)

    @override_settings(CELERY_BROKER_URL="memory://localhost/")
    @mock.patch('gis_app.signals.create_pdf_report_for_vehicles_task.apply_async')
    @mock.patch('gis_app.services.render_to_string')
    def test_vehicle_export(self, render_to_string_mock, create_pdf_report_for_vehicles_task_mock):
        vehicle_export = VehicleExportFactory()
        create_pdf_report_for_vehicles_task_mock.assert_called_with((vehicle_export.id, ), countdown=3)
        render_to_string_mock.return_value = self.expected_html
        create_pdf_report_for_vehicles_task(vehicle_export.id)
        render_to_string_mock.assert_called_with(mock.ANY, self.expected_values)
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


class PdfExportUserPositionTestCase(APITestCase):
    def setUp(self):
        super(PdfExportUserPositionTestCase, self).setUp()
        self.user = UserFactory()
        UserPositionFactory.create_batch(10, user=UserFactory())
        self.fields = ['id', 'user__username', 'position__lat', 'position__lon', 'fetch_time']
        self.qs = UserPosition.objects.all()
        self.expected_values = {"objects": list(self.qs.values(*self.fields))}
        self.expected_html = render_to_string("vehicle_export.html", self.expected_values)

    def test_pdf_export_to_string(self):
        exporter = PdfExport(self.qs, self.fields, "vehicle_export.html")
        html = exporter.export_to_string()
        self.assertEqual(html, self.expected_html)

    @override_settings(CELERY_BROKER_URL="memory://localhost/")
    @mock.patch('gis_app.signals.create_pdf_report_for_user_position_task.apply_async')
    @mock.patch('gis_app.services.render_to_string')
    def test_userposition_export(self, render_to_string_mock, create_pdf_report_for_user_position_task_mock):
        user_position_export = UserPositionExportFactory()
        create_pdf_report_for_user_position_task_mock.assert_called_with((user_position_export.id, ), countdown=3)
        render_to_string_mock.return_value = self.expected_html
        create_pdf_report_for_user_position_task(user_position_export.id)
        render_to_string_mock.assert_called_with(mock.ANY, self.expected_values)
        user_position_export.refresh_from_db()
        self.assertTrue(os.path.exists(user_position_export.file_path))
        self.assertEqual(user_position_export.status, "done")

    @override_settings(CELERY_BROKER_URL="memory://localhost/")
    @mock.patch('gis_app.models.UserPositionExport.set_status')
    @mock.patch('gis_app.signals.create_user_position_export_handler')
    def test_change_task_statuses(self, create_user_position_export_handler_mock, set_status_mock):
        user_position_export = UserPositionExportFactory()
        self.assertEqual(user_position_export.status, "new")
        create_pdf_report_for_user_position_task(user_position_export.id)
        set_status_mock.assert_has_calls([mock.call("creating"), mock.call("done")])
