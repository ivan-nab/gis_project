from django.contrib import admin
from gis_app.models import Location, UserPosition, UserAccount, Vehicle, UserVehicle, VehicleExport, Export


class VehicleExportAdmin(admin.ModelAdmin):
    readonly_fields = ['status', 'file_path']
    fields = ('status')


admin.site.register(Location)
admin.site.register(UserPosition)
admin.site.register(UserAccount)
admin.site.register(Vehicle)
admin.site.register(UserVehicle)
admin.site.register(VehicleExport)