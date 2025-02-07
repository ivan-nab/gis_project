from gis_project.celery import app

from .business_logic import (update_avg_coords, update_user_vehicles,
                             update_users_vehicles_names)
from .services import UserPositionReportMaker, VehicleReportMaker


@app.task
def update_avg_coords_task(userposition_id):
    return update_avg_coords(userposition_id)


@app.task
def update_users_vehicles_names_m2m_task(user_pk_set):
    return update_users_vehicles_names(user_pk_set)


@app.task
def update_user_vehicles_task(user_id):
    return update_user_vehicles(user_id)


@app.task
def create_pdf_report_for_vehicles_task(vehicle_export_id):
    return VehicleReportMaker().make_report(vehicle_export_id)


@app.task
def create_pdf_report_for_user_position_task(user_position_id):
    return UserPositionReportMaker().make_report(user_position_id)
