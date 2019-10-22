import requests
import json
import mz2geohash


def get_distance_from_openrouteservice(start, end):
    api_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    params = {
        "api_key": "5b3ce3597851110001cf62486763fa81a66e4f6eb844acb17ed611b2",
        "start": start,
        "end": end
    }
    response = requests.get(api_url, params=params)
    obj = json.loads(response.content)
    try:
        distance = obj['features'][0]['properties']['summary']['distance']
    except KeyError:
        return {"error": "error when fetching distance from external api"}
    return {"distance": distance}


def get_hash_for_coords(start, end):
    geo_hash = f"{mz2geohash.encode(start)}-{mz2geohash.encode(end)}"
    return geo_hash
