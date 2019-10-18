from django.apps import AppConfig
from django.db.models.signals import post_save, m2m_changed, post_delete
from .signals import update_avg_cords, update_user_vehicles_names_m2m, update_user_vehicles


class GisAppConfig(AppConfig):
    name = 'gis_app'

    def ready(self):
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
