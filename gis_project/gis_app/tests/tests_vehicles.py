from urllib.parse import urljoin
from unittest import mock

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, override_settings

from gis_app.serializers import VehicleSerializer

from .factories import UserFactory, VehicleFactory
from gis_app.business_logic import update_avg_coords, update_user_vehicles, update_users_vehicles_names


class VehiclesTestCase(APITestCase):

    url = reverse('vehicles-list')

    def setUp(self):
        super(VehiclesTestCase, self).setUp()
        self.user = UserFactory()
        self.vehicles = VehicleFactory.create_batch(3, users=(UserFactory(), ))
        self.user_vehicles = VehicleFactory.create_batch(2, users=(self.user, ))
        self.vehicles.extend(self.user_vehicles)
        self.data = VehicleSerializer(self.vehicles, many=True).data

    def test_get_vehicles(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('results'), self.data)

    @mock.patch('gis_app.signals.update_users_vehicles_names_m2m_task.apply_async')
    @mock.patch('gis_app.signals.update_user_vehicles_task.apply_async')
    def test_attach_user(self, update_user_vehicles_mock, update_users_vehicles_names_m2m_mock):
        self.client.force_authenticate(user=self.user)
        vehicle = self.vehicles[0]
        attach_url = urljoin(self.url, f'{vehicle.id}/attach_user/')
        response = self.client.post(attach_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attached_user = vehicle.users.get(id=self.user.id)
        self.assertEqual(attached_user, self.user)
        self.assertTrue(update_users_vehicles_names_m2m_mock.called)

    @mock.patch('gis_app.signals.update_users_vehicles_names_m2m_task.apply_async')
    @mock.patch('gis_app.signals.update_user_vehicles_task.apply_async')
    def test_detach_user(self, update_user_vehicles_mock, update_users_vehicles_names_m2m_mock):
        self.client.force_authenticate(user=self.user)
        vehicle = self.user_vehicles[0]
        detach_url = urljoin(self.url, f'{vehicle.id}/detach_user/')
        response = self.client.post(detach_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertRaises(User.DoesNotExist, lambda: vehicle.users.get(id=self.user.id))
        self.assertTrue(update_user_vehicles_mock.called)
        self.assertTrue(update_users_vehicles_names_m2m_mock.called)

    def test_attach_user_to_wrong_vehicle(self):
        self.client.force_authenticate(user=self.user)
        attach_url = urljoin(self.url, f'1000/attach_user/')
        response = self.client.post(attach_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detach_user_from_wrong_vehicle(self):
        self.client.force_authenticate(user=self.user)
        attach_url = urljoin(self.url, f'1000/detach_user/')
        response = self.client.post(attach_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
