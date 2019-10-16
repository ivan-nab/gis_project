from urllib.parse import urljoin

from rest_framework.test import APITestCase, RequestsClient

from .factories import UserFactory


class UserAuthTestCase(APITestCase):
    url = '/api-auth/login/'

    def setUp(self):
        self.password = '123'
        self.username = UserFactory.create(password=self.password).username

    def test_auth_with_requests(self):
        # Obtain a CSRF token.
        requests_client = RequestsClient()
        base_url = 'http://testserver'
        endpoint_url = urljoin(base_url, 'api-auth/login/')
        response = requests_client.get(endpoint_url)
        self.assertEqual(response.status_code, 200)
        csrftoken = response.cookies['csrftoken']

        response = requests_client.post(endpoint_url,
                                        headers={'X-CSRFToken': csrftoken},
                                        data={
                                            'username': self.username,
                                            'password': self.password
                                        },
                                        cookies={'csrftoken': csrftoken},
                                        allow_redirects=False)
        self.assertNotEqual(response.status_code, 403)
        self.assertNotEqual(response.status_code, 500)

    def test_auth_with_apiclient(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        csrftoken = response.cookies['csrftoken']
        self.client.cookies['csrftoken'] = csrftoken
        params = f'username={self.username}&password={self.password}'
        response = self.client.post(
            self.url,
            data=params,
            content_type='application/x-www-form-urlencoded',
            HTTP_X_CSRFTOKEN=csrftoken,
            follow=True)
        self.assertEqual(response.status_code, 302)
