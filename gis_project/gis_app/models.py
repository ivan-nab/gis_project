from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property


class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()


class UserAccount(User):
    vehicles = models.TextField()
    avg_coords = models.TextField()


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
