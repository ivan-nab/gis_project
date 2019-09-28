import json


def parse_geonames_csv(geonames_file):
    """
    Парсер файлов csv с сайта geonames.org

    :param: geonames_file: файл csv с именами

    :return: список словарей вида [{
        'name': 'Москва' - string
        'lat': 45.032, - float
        'lon': 56.083 - float
    }]
    """
    geonames = []
    with open(geonames_file, "rt", encoding="utf8") as fp:
        for line in fp:
            values = line.split('\t')
            location_name = values[3].split(",")[-1]
            if not location_name:
                location_name = values[2]
            geonames.append({
                'name': location_name,
                'lat': float(values[4]),
                'lon': float(values[5])
            })
    return geonames


def export_to_json(values, dest_json):
    with open(dest_json, "wt+") as fp:
        json.dump(values, fp)


if __name__ == "__main__":
    geonames = parse_geonames_csv("RU.txt")
    export_to_json(geonames, "locations.json")
