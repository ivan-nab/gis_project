import logging
import json

from django.urls import reverse
from django.contrib.auth import get_user_model
from gis_project.celery import app
from .models import UserPosition, UserAccount, UserVehicle


@app.task
def update_avg_cords_task(userposition_id):
    try:
        userposition = UserPosition.objects.get(pk=userposition_id)
        avg_coords = userposition.user.calculate_avg_coords()
        userposition.user.avg_coords = json.dumps(avg_coords)
        userposition.user.save()
    except UserPosition.DoesNotExist:
        logging.warning("Trying to get non existing userposition '%s'" %
                        userposition_id)


@app.task
def update_user_vehicles_names_m2m_task(user_pk_set):
    for pk in user_pk_set:
        user = UserAccount.objects.get(id=pk)
        vehicles_names = user.get_vehicles_names()
        user.vehicles = json.dumps(vehicles_names)
        user.save()


@app.task
def update_user_vehicles_task(uservehicle_id):
    user_vehicle = UserVehicle.objects.get(id=uservehicle_id)
    vehicles_names = user_vehicle.user.get_vehicles_names()
    user_vehicle.user.vehicles = json.dumps(vehicles_names)
    user_vehicle.user.save()
