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
        # В этом случае, наверное лучше сделать два тест кейса, тут два разных кейса тестируется.
        # А правило юнит тестов: Один кейс = один тест

        # этот теструет именно export_to_string, и больше ничего и не тестируется
        qs = Vehicle.objects.all()
        values = qs.values(*self.fields)
        expected_html = render_to_string("vehicle_export.html", {"objects": values})
        exporter = PdfExport(qs, self.fields, "vehicle_export.html")
        html = exporter.export_to_string()
        self.assertEqual(html, expected_html)

        # -----------

        # этот тестирует создание пути и статус.
        vehicle_export = VehicleExportFactory()
        # и может лучше мокать на более глубоком уровне ?
        # в иделае нужно бы мокать render_to_string_mock.assert_called_once_with(ANY, expected_values)
        mock_create_pdf_report_task.assert_called_once()
        # может тогда не придется уже вызывать create_pdf_report_for_vehicle(),
        # а получится одним тестом проверить весь цикл: Модель создали -> Экспорт появился.
        create_pdf_report_for_vehicle(vehicle_export.id)
        self.assertTrue(os.path.exists(vehicle_export.file_path))
        vehicle_export.refresh_from_db()
        self.assertEqual(vehicle_export.status, "done")
