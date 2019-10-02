import factory
from django.contrib.auth.models import User
from faker import Faker

from gis_app.models import Location, UserPosition

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
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
