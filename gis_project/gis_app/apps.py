from django.apps import AppConfig


class GisAppConfig(AppConfig):
    name = 'gis_app'

    def ready(self):
        from . import signals