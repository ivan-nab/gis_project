from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()


class UserPosition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Location,
                                 null=True,
                                 on_delete=models.SET_NULL)
    fetch_time = models.DateTimeField(default=timezone.now)


class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    speed = models.DecimalField(max_digits=4, decimal_places=0)
    users = models.ManyToManyField(User, through='UserVehicle')


class UserVehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'vehicle')
