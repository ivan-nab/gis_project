from django.apps import AppConfig
from django.db.models.signals import post_save
from .signals import update_avg_cords


class GisAppConfig(AppConfig):
    name = 'gis_app'

    def ready(self):
        post_save.connect(update_avg_cords,
                          sender="gis_app.UserPosition",
                          dispatch_uid="update_avg_coords")
