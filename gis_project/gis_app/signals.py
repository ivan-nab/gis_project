import json
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed, post_delete


@receiver(post_save,
          sender="gis_app.UserPosition",
          dispatch_uid="update_avg_coords")
def update_avg_cords(sender, instance, **kwargs):
    avg_coords = instance.user.calculate_avg_coords()
    instance.user.avg_coords = json.dumps(avg_coords)
    instance.user.save()


@receiver(m2m_changed,
          sender="gis_app.UserVehicle",
          dispatch_uid="update_user_vehicles_names_m2m")
def update_user_vehicles_names_m2m(sender, instance, action, **kwargs):
    user_pk_set = kwargs["pk_set"]
    model = kwargs["model"]
    if action in ["post_add", "post_remove"]:
        for pk in user_pk_set:
            user = model.objects.get(id=pk)
            vehicles_names = user.get_vehicles_names()
            user.vehicles = json.dumps(vehicles_names)
            user.save()


@receiver([post_save, post_delete],
          sender="gis_app.UserVehicle",
          dispatch_uid="update_user_vehicles")
def update_user_vehicles(sender, instance, **kwargs):
    vehicles_names = instance.user.get_vehicles_names()
    instance.user.vehicles = json.dumps(vehicles_names)
    instance.user.save()
