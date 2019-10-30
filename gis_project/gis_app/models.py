from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()


class UserAccount(User):
    vehicles = models.TextField()
    avg_coords = models.TextField()

    def calculate_avg_coords(self, start_time=None, end_time=None):
        qs = UserPosition.objects.filter(user_id=self.id)
        if start_time:
            qs = qs.filter(fetch_time__gte=start_time)
        if end_time:
            qs = qs.filter(fetch_time__lte=end_time)
        return qs.values('position__lon',
                         'position__lat').aggregate(lon=Avg('position__lon'),
                                                    lat=Avg('position__lat'))

    def get_vehicles_names(self):
        return list(UserVehicle.objects.filter(user_id=self.id).values_list(
            'vehicle__name', flat=True))


class UserPosition(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    position = models.ForeignKey(Location,
                                 null=True,
                                 on_delete=models.SET_NULL)
    fetch_time = models.DateTimeField(default=timezone.now)


class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    speed = models.DecimalField(max_digits=4, decimal_places=0)
    users = models.ManyToManyField(UserAccount, through='UserVehicle')


class UserVehicle(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'vehicle')

        # @cached_property
        # def vehicles(self):
        #     return list(self.vehicle_set.values_list('name', flat=True))

        # @cached_property
        # def avg_coords(self):
        #     return self.userposition_set.get_queryset().objects.values(
        #         'position__lon',
        #         'position__lat').aggregate(lon=Avg('position__lon'),
        #                                    lat=Avg('position__lat'))
