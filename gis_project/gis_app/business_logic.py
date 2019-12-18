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
