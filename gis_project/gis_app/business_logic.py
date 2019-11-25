import json
import logging
import os
import uuid

from django.conf import settings

from .models import UserAccount, UserPosition, VehicleExport, UserPositionExport
from .services import UserPositionPdfExport, VehiclePdfExport


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


def make_pdf(instance, exporter):
    instance.set_status("creating")
    if not instance.file_path:
        instance.file_path = os.path.join(settings.PDF_EXPORTS_DIR, f"{uuid.uuid4()}.pdf")
    exporter.export_to_pdf(instance.file_path)
    instance.set_status("done")


def create_pdf_report_for_vehicle(vehicle_export_id):
    try:
        vehicle_export_instance = VehicleExport.objects.get(id=vehicle_export_id)
    except VehicleExport.DoesNotExist:
        logging.warning("Trying to get non existing vehicle export'%s'" % vehicle_export_id)
    else:
        make_pdf(vehicle_export_instance, VehiclePdfExport())


def create_pdf_report_for_user_position(user_position_id):
    try:
        user_position_export_instance = UserPositionExport.objects.get(id=user_position_id)
    except UserPositionExport.DoesNotExist:
        logging.warning("Trying to get non existing user position'%s'" % user_position_id)
    else:
        make_pdf(user_position_export_instance, UserPositionPdfExport())
