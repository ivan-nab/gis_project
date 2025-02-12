from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .tasks import (update_avg_coords_task, update_user_vehicles_task, update_users_vehicles_names_m2m_task,
                    create_pdf_report_for_vehicles_task, create_pdf_report_for_user_position_task)


@receiver(post_save, sender="gis_app.UserPosition", dispatch_uid="update_avg_coords")
def update_avg_coords(sender, instance, **kwargs):
    update_avg_coords_task.apply_async((instance.id, ), countdown=10)


@receiver(m2m_changed, sender="gis_app.UserVehicle", dispatch_uid="update_user_vehicles_names_m2m")
def update_user_vehicles_names_m2m(sender, instance, action, **kwargs):
    user_pk_set = kwargs["pk_set"]
    if action in ["post_add", "post_remove"]:
        update_users_vehicles_names_m2m_task.apply_async((list(user_pk_set), ), countdown=10)


@receiver([post_save, post_delete], sender="gis_app.UserVehicle", dispatch_uid="update_user_vehicles")
def update_user_vehicles(sender, instance, **kwargs):
    update_user_vehicles_task.apply_async((instance.user.id, ), countdown=10)


@receiver(post_save, sender="gis_app.VehicleExport", dispatch_uid="create_vehicle_export_handler")
def create_vehicle_export_handler(sender, instance, **kwargs):
    if kwargs['created']:
        create_pdf_report_for_vehicles_task.apply_async((instance.id, ), countdown=3)


@receiver(post_save, sender="gis_app.UserPositionExport", dispatch_uid="create_user_position_export_handler")
def create_user_position_export_handler(sender, instance, **kwargs):
    if kwargs['created']:
        create_pdf_report_for_user_position_task.apply_async((instance.id, ), countdown=3)
