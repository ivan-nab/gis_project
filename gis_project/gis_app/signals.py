import json
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed, post_delete
from .tasks import update_avg_coords_task, update_users_vehicles_names_m2m_task, update_user_vehicles_task

@receiver(post_save,
          sender="gis_app.UserPosition",
          dispatch_uid="update_avg_coords")
def update_avg_coords(sender, instance, **kwargs):
    update_avg_coords_task.delay(instance.id)


@receiver(m2m_changed,
          sender="gis_app.UserVehicle",
          dispatch_uid="update_user_vehicles_names_m2m")
def update_user_vehicles_names_m2m(sender, instance, action, **kwargs):
    user_pk_set = kwargs["pk_set"]
    if action in ["post_add", "post_remove"]:
        update_users_vehicles_names_m2m_task.delay(list(user_pk_set))
 


@receiver([post_save, post_delete],
          sender="gis_app.UserVehicle",
          dispatch_uid="update_user_vehicles")
def update_user_vehicles(sender, instance, **kwargs):
    update_user_vehicles_task.delay(instance.user.id)

