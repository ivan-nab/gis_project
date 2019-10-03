from urllib.parse import urljoin
from rest_framework.test import APITestCase, RequestsClient

from .factories import UserFactory


class UserAuthTestCase(APITestCase):
    def setUp(self):
        self.password = '123'
        self.username = UserFactory.create(password=self.password).username
        self.client = RequestsClient()

    def test_auth_with_requests(self):
        # Obtain a CSRF token.
        base_url = 'http://testserver'
        endpoint_url = urljoin(base_url, 'api-auth/login/')
        response = self.client.get(endpoint_url)
        self.assertEqual(response.status_code, 200)
        csrftoken = response.cookies['csrftoken']
        #endpoint_url = urllib.parse.urljoin(base_url, reverse(self.url))

        response = self.client.post(endpoint_url,
                                    headers={'X-CSRFToken': csrftoken},
                                    data={
                                        'username': self.username,
                                        'password': self.password
                                    },
                                    cookies={'csrftoken': csrftoken},
                                    allow_redirects=False)
        self.assertNotEqual(response.status_code,403)
        self.assertNotEqual(response.status_code,500)

