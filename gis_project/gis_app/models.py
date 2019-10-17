from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.db.models.signals import post_save, m2m_changed, post_delete
from .signals import update_avg_cords, update_user_vehicles_names_m2m, update_user_vehicles


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
        return list(self.vehicle_set.get_queryset().values_list('name',
                                                                flat=True))


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


post_save.connect(update_avg_cords,
                  sender="gis_app.UserPosition",
                  dispatch_uid="update_avg_coords")

m2m_changed.connect(update_user_vehicles_names_m2m,
                    sender="gis_app.UserVehicle",
                    dispatch_uid="update_user_vehicles_names_m2m")

post_save.connect(update_user_vehicles,
                  sender="gis_app.UserVehicle",
                  dispatch_uid="update_user_vehicles")

post_delete.connect(update_user_vehicles,
                  sender="gis_app.UserVehicle",
                  dispatch_uid="update_user_vehicles")