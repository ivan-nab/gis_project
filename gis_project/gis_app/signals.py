import json
from django.db.models.signals import post_save
from django.dispatch import receiver

from gis_app.models import UserPosition, UserVehicle


@receiver(post_save, sender=UserPosition, dispatch_uid="update_avg_coords")
def update_avg_cords(sender, instance, **kwargs):
    print("update")
    avg_coords = instance.user.calculate_avg_coords()
    instance.user.avg_coords = json.dumps(avg_coords)
    instance.user.save()
