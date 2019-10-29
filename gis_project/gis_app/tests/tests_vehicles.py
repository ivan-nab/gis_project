from urllib.parse import urljoin

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase,override_settings

from gis_app.serializers import VehicleSerializer

from .factories import UserFactory, VehicleFactory


class VehiclesTestCase(APITestCase):

    url = reverse('vehicles-list')

    def setUp(self):
        super(VehiclesTestCase, self).setUp()
        self.user = UserFactory()
        self.vehicles = VehicleFactory.create_batch(3, users=(UserFactory(), ))
        self.user_vehicles = VehicleFactory.create_batch(2,
                                                         users=(self.user, ))
        self.vehicles.extend(self.user_vehicles)
        self.data = VehicleSerializer(self.vehicles, many=True).data

    def test_get_vehicles(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('results'), self.data)

    def test_attach_user(self):
        self.client.force_authenticate(user=self.user)
        vehicle = self.vehicles[0]
        attach_url = urljoin(self.url, f'{vehicle.id}/attach_user/')
        response = self.client.post(attach_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attached_user = vehicle.users.get(id=self.user.id)
        self.assertEqual(attached_user, self.user)

    def test_detach_user(self):
        self.client.force_authenticate(user=self.user)
        vehicle = self.user_vehicles[0]
        detach_url = urljoin(self.url, f'{vehicle.id}/detach_user/')
        response = self.client.post(detach_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertRaises(User.DoesNotExist,
                          lambda: vehicle.users.get(id=self.user.id))

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
