import urllib.parse
from statistics import mean

from django.contrib.auth.models import User
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase, RequestsClient

from gis_app.serializers import UserPositionSerializer, UserSummarySerializer

from .factories import LocationFactory, UserFactory, UserPositionFactory


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
        self.avg_lat = mean([l.lat for l in self.locations])
        self.avg_lon = mean([l.lon for l in self.locations])

        self.user_positions = [
            UserPositionFactory(user=self.user, position=pos)
            for pos in self.locations
        ]

        self.data = UserSummarySerializer(self.user).data

    def test_get_user_summary(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        summary_info = response.data['results'][0]
        self.assertEqual(summary_info, self.data)
        avg_coords = summary_info['avg_coords']
        self.assertEqual(round(float(avg_coords['lon']), 3),
                         round(float(self.avg_lon), 3))
        self.assertEqual(round(float(avg_coords['lat']), 3),
                         round(float(self.avg_lat), 3))

        # # Obtain a CSRF token.
        # base_url = 'http://testserver'
        # endpoint_url = urllib.parse.urljoin(base_url, 'api-auth/login/')
        # response = client.get(endpoint_url)
        # user = self.users[0]
        # assert response.status_code == 200
        # csrftoken = response.cookies['csrftoken']
        # #endpoint_url = urllib.parse.urljoin(base_url, reverse(self.url))

        # response = client.post(endpoint_url,
        #                        headers={'X-CSRFToken': csrftoken},
        #                        data={
        #                            'username': user.username,
        #                            'password': user.password
        #                        },
        #                        cookies={'csrftoken': csrftoken},
        #                        allow_redirects=False)
        # assert response.status_code != 403
        # print(response.status_code)
