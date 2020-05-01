from haystack import connections
from haystack.utils.loading import ConnectionHandler, UnifiedIndex
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, override_settings

from gis_app.models import Location, Vehicle
from gis_app.search_indexes import LocationIndex, VehicleIndex

from .factories import LocationFactory, UserFactory, VehicleFactory

TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine',
        'URL': 'http://elastic:changeme@elastic:9200/',
        'INDEX_NAME': 'haystack-test',
    },
}


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class SearchTest(APITestCase):

    locations_url = reverse('locations-search-list')
    vehicles_url = reverse('vehicles-search-list')
    search_url = reverse('search-list')

    def setUp(self):
        connections = ConnectionHandler(TEST_INDEX)
        super(SearchTest, self).setUp()

        self.user = UserFactory()
        self.first_location = LocationFactory(name='first Location')
        self.second_location = LocationFactory(name='second Location')
        self.first_vehicle = VehicleFactory(name='first Vehicle')
        self.second_vehicle = VehicleFactory(name='second Vehicle')

        # Stow.
        self.old_unified_index = connections['default']._index
        self.ui = UnifiedIndex()
        self.location_index = LocationIndex()
        self.vehicle_index = VehicleIndex()
        self.ui.build(indexes=[self.location_index, self.vehicle_index])
        connections['default']._index = self.ui

        # Update the 'index'.
        backend = connections['default'].get_backend()
        backend.clear()
        backend.update(self.location_index, Location.objects.all())
        for obj in Location.objects.all():
            print(obj.name, obj.id)

        backend.update(self.vehicle_index, Vehicle.objects.all())

    def tearDown(self):
        connections['default']._index = self.old_unified_index
        super(SearchTest, self).tearDown()

    @override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
    def test_search_locations(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.locations_url, {'name_auto': 'first'})

        self.assertEqual(self.first_location.name, response.data['results'][0]['name'])
        response = self.client.get(self.locations_url, {'name_auto': 'second'})

        self.assertEqual(self.second_location.name, response.data['results'][0]['name'])

        response = self.client.get(self.locations_url, {'name': self.first_location.name})
        self.assertEqual(self.first_location.name, response.data['results'][0]['name'])

        response = self.client.get(self.locations_url, {'name': self.second_location.name})
        self.assertEqual(self.second_location.name, response.data['results'][0]['name'])

    def test_search_vehicles(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.vehicles_url, {'name_auto': 'first'})
        self.assertEqual(self.first_vehicle.name, response.data['results'][0]['name'])

        response = self.client.get(self.vehicles_url, {'name_auto': 'second'})
        self.assertEqual(self.second_vehicle.name, response.data['results'][0]['name'])

        response = self.client.get(self.vehicles_url, {'name': self.first_vehicle.name})
        self.assertEqual(self.first_vehicle.name, response.data['results'][0]['name'])

        response = self.client.get(self.vehicles_url, {'name': self.second_vehicle.name})
        self.assertEqual(self.second_vehicle.name, response.data['results'][0]['name'])

    def test_search_aggregate(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.search_url, {'q': 'first'})
        self.assertEqual({self.first_vehicle.name, self.first_location.name},
                         {response.data['results'][0]['name'], response.data['results'][1]['name']})

        response = self.client.get(self.search_url, {'q': 'second'})
        self.assertEqual({self.second_vehicle.name, self.second_location.name},
                         {response.data['results'][0]['name'], response.data['results'][1]['name']})
