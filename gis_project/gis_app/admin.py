from django.contrib import admin
from gis_app.models import Location, UserPosition, UserAccount

admin.site.register(Location)
admin.site.register(UserPosition)
admin.site.register(UserAccount)