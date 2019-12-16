from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.urls import reverse

class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()

    def get_absolute_url(self):
        return reverse('locations-detail', args=[str(self.id)])

class UserAccount(User):
    vehicles = models.TextField()
    avg_coords = models.TextField()

    def calculate_avg_coords(self, start_time=None, end_time=None):
        qs = UserPosition.objects.filter(user_id=self.id)
        if start_time:
            qs = qs.filter(fetch_time__gte=start_time)
        if end_time:
            qs = qs.filter(fetch_time__lte=end_time)
        return qs.values('position__lon', 'position__lat').aggregate(lon=Avg('position__lon'), lat=Avg('position__lat'))

    def get_vehicles_names(self):
        return list(UserVehicle.objects.filter(user_id=self.id).values_list('vehicle__name', flat=True))


class UserPosition(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    position = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    fetch_time = models.DateTimeField(default=timezone.now)


class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    speed = models.DecimalField(max_digits=4, decimal_places=0)
    users = models.ManyToManyField(UserAccount, through='UserVehicle')
    
    def get_absolute_url(self):
        return reverse('vehicles-detail', args=[str(self.id)])

class UserVehicle(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'vehicle')


class Export(models.Model):
    status = models.CharField(choices=(('new', 'New'), ('creating', 'Creating'), ('done', 'Done')),
                              default='new',
                              max_length=255)
    file_path = models.FilePathField(path=settings.PDF_EXPORTS_DIR, match=r".*\.pdf$", max_length=255, blank=True)

    class Meta:
        abstract = True

    def set_status(self, status):
        self.status = status
        self.save()


class VehicleExport(Export):
    def get_export_model_queryset(self):
        return Vehicle.objects.all()


class UserPositionExport(Export):
    def get_export_model_queryset(self):
        return UserPosition.objects.all()
