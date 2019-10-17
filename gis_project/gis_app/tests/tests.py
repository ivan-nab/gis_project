from statistics import mean
from urllib.parse import urljoin

from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from gis_app.serializers import UserPositionSerializer, UserSummarySerializer

from .factories import (LocationFactory, UserFactory, UserPositionFactory,
                        VehicleFactory)


class UserPositionTestCase(APITestCase):

    url = reverse('user-position-list')

    def setUp(self):
        super(UserPositionTestCase, self).setUp()
        self.users = UserFactory.create_batch(2)
        self.first_user_positions = \
            UserPositionFactory.create_batch(2, user=self.users[0])
        self.second_user_positions = \
            UserPositionFactory.create_batch(2, user=self.users[1])

        self.data = UserPositionSerializer(self.first_user_positions,
                                           many=True).data

    def test_get_userpositions(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('results'), self.data)

    def test_create_userposition(self):
        self.client.force_authenticate(user=self.users[0])
        new_userposition = UserPositionFactory(user=self.users[0])
        data = UserPositionSerializer(new_userposition).data
        response = self.client.post(self.url, data)
        data['id'] = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data, response.data)

    def test_get_userpositions_unauthorized(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserSummaryTestCase(APITestCase):
    url = reverse('user-summary-list')

    def setUp(self):
        super(UserSummaryTestCase, self).setUp()
        self.user = UserFactory()
        self.locations = LocationFactory.create_batch(3)
        self.user_vehicles = VehicleFactory.create_batch(2,
                                                         users=(self.user, ))
        self.vehicles = VehicleFactory.create_batch(3, users=(UserFactory(), ))
        self.start_time = parse_datetime("2019-10-01T00:00:00Z")
        self.mid_time = parse_datetime("2019-10-02T00:00:00Z")
        self.end_time = parse_datetime("2019-10-03T00:00:00Z")
        self.wrong_time = parse_datetime("2029-10-03T00:00:00Z")
        self.user_positions = [
            UserPositionFactory(user=self.user,
                                position=self.locations[0],
                                fetch_time=self.start_time),
            UserPositionFactory(user=self.user,
                                position=self.locations[1],
                                fetch_time=self.mid_time),
            UserPositionFactory(user=self.user,
                                position=self.locations[2],
                                fetch_time=self.end_time),
        ]
        self.avg_coords = {
            'lat': mean([l.lat for l in self.locations]),
            'lon': mean([l.lon for l in self.locations])
        }
        self.avg_coords_start_mid = {
            'lat': mean([self.locations[0].lat, self.locations[1].lat]),
            'lon': mean([self.locations[0].lon, self.locations[1].lon])
        }
        self.avg_coords_mid_end = {
            'lat': mean([self.locations[1].lat, self.locations[2].lat]),
            'lon': mean([self.locations[1].lon, self.locations[2].lon])
        }
        self.data = UserSummarySerializer(self.user).data

    def test_get_user_summary(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        summary_info = response.data['results'][0]
        self.assertEqual(summary_info, self.data)
        coords = summary_info['avg_coords']
        self.assertEqual(round(float(coords['lon']), 3),
                         round(float(self.avg_coords['lon']), 3))
        self.assertEqual(round(float(coords['lat']), 3),
                         round(float(self.avg_coords['lat']), 3))

    def test_get_user_summary_with_params(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {
            'start_time': self.start_time,
            'end_time': self.start_time
        })
        coords = response.data['results'][0]['avg_coords']
        self.assertEqual(round(float(coords['lat']), 3),
                         round(float(self.locations[0].lat), 3))

        response = self.client.get(self.url, {
            'start_time': self.start_time,
            'end_time': self.mid_time
        })
        coords = response.data['results'][0]['avg_coords']
        self.assertEqual(round(float(coords['lon']), 3),
                         round(float(self.avg_coords_start_mid['lon']), 3))

        response = self.client.get(self.url, {
            'start_time': self.mid_time,
            'end_time': self.end_time
        })
        coords = response.data['results'][0]['avg_coords']
        self.assertEqual(round(float(coords['lat']), 3),
                         round(float(self.avg_coords_mid_end['lat']), 3))

        response = self.client.get(self.url, {
            'start_time': self.wrong_time,
            'end_time': self.wrong_time
        })
        coords = response.data['results'][0]['avg_coords']
        self.assertEqual(None, coords['lat'])
        self.assertEqual(None, coords['lon'])

    def test_user_vehicles_names(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        summary_info = response.data['results'][0]
        received_vehicles_names = summary_info['vehicles']
        self.assertIsNotNone(self.user.vehicles)
        self.assertEqual(received_vehicles_names,
                         [v.name for v in self.user_vehicles])

    def test_user_vehicles_names_cache(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        summary_info = response.data['results'][0]
        received_vehicles_names = summary_info['vehicles']
        vehicle = self.vehicles[0]
        attach_url = urljoin(reverse('vehicles-list'),
                             f'{vehicle.id}/attach_user/')
        response = self.client.post(attach_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url)
        summary_info = response.data['results'][0]
        new_vehicle_names = summary_info['vehicles']
        self.assertIsNotNone(new_vehicle_names)
        self.assertNotEqual(received_vehicles_names, new_vehicle_names)

    def test_user_avg_coords_cache(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        summary_info = response.data['results'][0]
        coords = summary_info['avg_coords']
        UserPositionFactory(user=self.user)
        response = self.client.get(self.url)
        summary_info = response.data['results'][0]
        new_coords = summary_info['avg_coords']
        self.assertNotEqual(coords, new_coords)
