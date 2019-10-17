import json


def update_avg_cords(sender, instance, **kwargs):
    avg_coords = instance.user.calculate_avg_coords()
    instance.user.avg_coords = json.dumps(avg_coords)
    instance.user.save()


def update_user_vehicles_names_m2m(sender, instance, action, **kwargs):
    user_pk_set = kwargs["pk_set"]
    model = kwargs["model"]
    if action in ["post_add", "post_remove"]:
        for pk in user_pk_set:
            user = model.objects.get(id=pk)
            vehicles_names = user.get_vehicles_names()
            user.vehicles = json.dumps(vehicles_names)
            user.save()


def update_user_vehicles(sender, instance, **kwargs):
    vehicles_names = instance.user.get_vehicles_names()
    instance.user.vehicles = json.dumps(vehicles_names)
    instance.user.save()