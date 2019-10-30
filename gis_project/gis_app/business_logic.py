import logging
import json

from .models import UserPosition, UserAccount, UserVehicle


def update_avg_coords(userposition_id):
    try:
        userposition = UserPosition.objects.get(pk=userposition_id)
        avg_coords = userposition.user.calculate_avg_coords()
        userposition.user.avg_coords = json.dumps(avg_coords)
        userposition.user.save()
    except UserPosition.DoesNotExist:
        logging.warning("Trying to get non existing userposition '%s'" %
                        userposition_id)

def update_users_vehicles_names(user_pk_set):
    return [update_user_vehicles(pk) for pk in user_pk_set]

def update_user_vehicles(user_id):
    try:
        user = UserAccount.objects.get(id=user_id)
        vehicles_names = user.get_vehicles_names()
        user.vehicles = json.dumps(vehicles_names)
        user.save()
    except UserAccount.DoesNotExist:
        logging.warning("Trying to get non existing user account'%s'" %
                        user_id)
    else:
        return {
            "user_id": user.id,
            "vehicles_names": vehicles_names
        }
