import json
from datetime import datetime
from urllib.parse import urljoin

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, override_settings

from gis_app.serializers import VehicleSerializer
from unittest import mock

from .factories import LocationFactory, UserFactory, UserPositionFactory


class DistanceTestCase(APITestCase):

    url = reverse('distance-list')

    def setUp(self):
        super(DistanceTestCase, self).setUp()
        self.user = UserFactory()
        first_location = LocationFactory(lat=55.721986, lon=37.555218)
        second_location = LocationFactory(lat=55.736969, lon=37.552643)
        UserPositionFactory(user=self.user, position=second_location)
        UserPositionFactory(user=self.user,
                            position=first_location,
                            fetch_time=datetime.now())
        self.end_coords = "55.765855,37.53788"

        with open("gis_app/tests/data/routes_response_good.json", "rt") as fp:
            self.good_response_json = fp.read()



    @mock.patch("gis_app.services.requests.get")
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
        }
    })
    def test_get_distance(self, mock_get):
        self.client.force_authenticate(self.user)

        mock_get.return_value.content = self.good_response_json
        mock_get.return_value.status_code = 200

        response = self.client.get(self.url, {'end': self.end_coords})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('distance'))
        self.assertEqual(response.data.get('distance'), 4984.9)
        mock_get.assert_called_once()

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
        }
    })
    @mock.patch("gis_app.services.requests.get")
    def test_save_distance_to_cache(self, mock_get):
        self.client.force_authenticate(self.user)
        mock_get.return_value.content = self.good_response_json
        mock_get.return_value.status_code = 200
        with mock.patch('gis_app.views.cache') as mock_cache:
            mock_cache.get.return_value = None
            response = self.client.get(self.url, {'end': self.end_coords})
            self.assertEqual(mock_cache.set.call_count, 1)

    @mock.patch("gis_app.services.requests.get")
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
        }
    })
    def test_get_distance_from_cache(self, mock_get):
        self.client.force_authenticate(self.user)
        mock_get.return_value.content = self.good_response_json
        mock_get.return_value.status_code = 200
        with mock.patch('gis_app.views.cache') as mock_cache:
            mock_cache.get.return_value = {'distance': 4984.9}
            response = self.client.get(self.url, {'end': self.end_coords})
            self.assertEqual(mock_cache.get.call_count, 1)
            self.assertEqual(response.data, mock_cache.get.return_value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get.assert_not_called()