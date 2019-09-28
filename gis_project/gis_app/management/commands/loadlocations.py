from django.core.management.base import BaseCommand

from gis_app.models import Location
from common.util.geonames_parser import parse_geonames_csv


class Command(BaseCommand):
    help = 'Loads locations from geonames csv file'

    def add_arguments(self, parser):
        parser.add_argument('locations_file', type=str)

    def handle(self, *args, **options):
        locations_file = options.get('locations_file')
        locations = self._import_locations(locations_file)
        if locations:
            result = self._create_locations(locations)
            if result:
                self.stdout.write(
                    self.style.SUCCESS('Locations imported succesfull'))

    def _import_locations(self, locations_file):
        locations = parse_geonames_csv(locations_file)
        if locations:
            objs = [
                Location(name=l['name'], lat=l['lat'], lon=l['lon'])
                for l in locations
            ]
            return objs

    def _create_locations(self, locations):
        return Location.objects.bulk_create(locations)
