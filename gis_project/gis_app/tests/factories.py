import factory
import tempfile
import os
from faker import Faker

from gis_app.models import Location, UserPosition, Vehicle, UserAccount, VehicleExport

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserAccount
        django_get_or_create = ('username', )

    username = factory.LazyAttribute(
        lambda obj: faker.simple_profile()['username'])
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    password = faker.password()


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = faker.city()
    lat = factory.LazyAttribute(lambda obj: faker.latitude())
    lon = factory.LazyAttribute(lambda obj: faker.longitude())


class UserPositionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserPosition

    user = factory.SubFactory(UserFactory)
    position = factory.SubFactory(LocationFactory)
    fetch_time = factory.LazyAttribute(
        lambda obj: faker.past_datetime(start_date="-30d", tzinfo=None))


class VehicleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vehicle

    name = factory.LazyAttribute(lambda obj: faker.name())

    speed = factory.LazyAttribute(lambda obj: faker.random_int(min=0, max=999))

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)


class VehicleExportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VehicleExport

    file_path = factory.LazyAttribute(lambda obj: os.path.join(tempfile.gettempdir(), faker.file_name(extension="pdf")))
