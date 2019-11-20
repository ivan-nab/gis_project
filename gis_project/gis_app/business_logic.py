import json
import logging

from .models import UserAccount, UserPosition, VehicleExport
from .services import PdfExport

def update_avg_coords(userposition_id):
    try:
        userposition = UserPosition.objects.get(pk=userposition_id)
    except UserPosition.DoesNotExist:
        logging.warning("Trying to get non existing userposition '%s'" % userposition_id)
    else:
        avg_coords = userposition.user.calculate_avg_coords()
        userposition.user.avg_coords = json.dumps(avg_coords)
        userposition.user.save()


def update_users_vehicles_names(user_pk_set):
    for pk in user_pk_set:
        update_user_vehicles(pk)


def update_user_vehicles(user_id):
    try:
        user = UserAccount.objects.get(id=user_id)
    except UserAccount.DoesNotExist:
        logging.warning("Trying to get non existing user account'%s'" % user_id)
    else:
        vehicles_names = user.get_vehicles_names()
        user.vehicles = json.dumps(vehicles_names)
        user.save()


def make_pdf(instance, fields, template):
    qs = instance.get_export_model_queryset()
    exporter = PdfExport(qs, fields, template)
    instance.status = "creating"
    instance.save()
    result = exporter.export_to_pdf(instance.file_path)
    instance.status = "done"
    instance.save()
    return result


def create_pdf_report_for_vehicle(vehicle_export_id):
    try:
        vehicle_export = VehicleExport.objects.get(id=vehicle_export_id)
    except VehicleExport.DoesNotExist:
        logging.warning("Trying to get non existing vehicle export'%s'" % vehicle_export_id)
    else:
        make_pdf(vehicle_export, ['id', 'name'], "vehicle_export.html")

