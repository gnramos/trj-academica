import pandas as pd
import requests
import time
import json
import sys
import re
import os


def write_json(json_info, file):
    """Write the json_info in file."""
    with open(file, 'w+') as outfile:
        json.dump(json_info, outfile,
                  indent=4, sort_keys=True, ensure_ascii=False)


def read_json(file):
    """Read the json from file, return a empty json if file doesn't exist."""
    if os.path.isfile(file):
        with open(file, 'r') as outfile:
            return json.load(outfile)
    return json.loads('{}')


def google_maps_key():
    """Read the Google Maps API key from the key file."""
    with open('key', 'r') as f:
        return f.read()


def format_cep(cep):
    """Remove the non-numeric characters and add trailing zeros in cep."""
    return re.sub('[^0-9]', '', str(cep)).ljust(8, '0')


def unique_ceps(df_file):
    """Return a list of unique cep values from the database."""

    column_name = 'cep'
    df = pd.read_csv(df_file, sep=';', low_memory=False)
    cep_list = df[column_name].dropna().tolist()
    cep_list = [format_cep(cep) for cep in cep_list]
    cep_list = list(dict.fromkeys(cep_list))  # drop duplicates
    return cep_list


def request_address(cep_list, address_json_file):
    """
    Request address information for all ceps in cep_list
    which haven't been requested yet, using ViaCEP Web Service.
    Generate a json file with the data requested.
    """

    def via_cep(cep):
        """Request cep address information using the ViaCEP Web Service."""
        url = f'https://viacep.com.br/ws/{cep}/json/'
        return json.loads(requests.get(url).text)

    address_json = read_json(address_json_file)
    gen = (cep for cep in cep_list if cep not in address_json)  # generator exp
    for cep in gen:

        try:
            print(f'Requesting address: {cep}')

            time.sleep(4)  # Just so viacep don't block us.
            address_info = via_cep(cep)
            address_json[cep] = address_info
            if 'erro' in address_info:
                raise ValueError("CEP not found.")

            print(f'Done.')

        except KeyboardInterrupt:
            write_json(address_json, address_json_file)
            sys.exit()

        except Exception as e:
            print(f'Error requesting {cep}: {e}')

    write_json(address_json, address_json_file)
    return address_json


def request_coordinate(cep_list, address_json_file, coordinate_json_file):
    """
    Request coordinate information for all ceps in cep_list
    which haven't been requested yet,
    using Geocoding API from Google Maps Plataform.
    Generate a json file with the data requested.
    """

    def geocoding(address):
        """
        Request coordinate info using Geocoding.
        Use a bounding box containing DF, to better locate the addresses.
        """
        bounding_box = '-16.075488,-48.27116|-15.474912,-47.313024'
        request = requests.get(
            f'https://maps.googleapis.com/maps/api/geocode/json'
            f'?language=pt-BR'
            f'&bounds={bounding_box}'
            f'&address={address}'
            f'&key={google_maps_key()}'
        )
        return json.loads(request.text)

    def get_address(cep, address_json):
        """Return the address of cep."""
        info = address_json[cep]
        # address = ['bairro', 'uf']
        address = ['logradouro', 'bairro', 'uf']

        return " ".join(info[item] for item in address)

    address_json = read_json(address_json_file)
    coordinate_json = read_json(coordinate_json_file)
    gen = (cep for cep in cep_list if (
        cep not in coordinate_json and
        cep in address_json and
        'erro' not in address_json[cep]
    ))

    for cep in gen:

        try:
            print(f'Requesting coordinate: {cep}')

            address = get_address(cep, address_json)
            coordinate_info = geocoding(address)
            if coordinate_info['status'] != 'OK':
                raise ValueError("Address not found.")
            coordinate_json[cep] = \
                coordinate_info['results'][0]['geometry']['location']

            print('Done.')
        except KeyboardInterrupt:
            write_json(coordinate_json, coordinate_json_file)
            sys.exit()

        except Exception as e:
            print(f'Error requesting {cep}: {e}')

    write_json(coordinate_json, coordinate_json_file)
    return coordinate_json


def request_route(cep_list, coordinate_json_file, route_json_file):
    """
    Request route between University of Brasilia (UnB) and cep's coordinates
    for all ceps in cep_list which haven't been requested yet,
    using Distance Matrix API from Google Maps Plataform.
    Generate a json file with the data requested.
    """

    def distance_matrix(coordinate1, coordinate2):
        """Request route info using Distance Matrix."""
        request = requests.get(
                f'https://maps.googleapis.com/maps/api/distancematrix/json'
                f'?units=metric'
                f'&language=pt-BR'
                f'&origins={coordinate1}'
                f'&destinations={coordinate2}'
                f'&key={google_maps_key()}')

        return json.loads(request.text)

    coordinate_json = read_json(coordinate_json_file)
    route_json = read_json(route_json_file)

    gen = (cep for cep in cep_list if (
        cep not in route_json and
        cep in coordinate_json
    ))
    for cep in gen:

        try:
            print(f'Requesting route: {cep}')

            coordinate1 = ','.join([
                str(coordinate_json[cep]['lat']),
                str(coordinate_json[cep]['lng'])
            ])
            coordinateUNB = '-15.763023,-47.871255'

            route_info = distance_matrix(coordinate1, coordinateUNB)
            if route_info['status'] != 'OK':
                raise ValueError("Coordinates not found.")
            route_json[cep] = route_info['rows'][0]['elements'][0]

            print('Done.')

        except KeyboardInterrupt:
            write_json(route_json, route_json_file)
            sys.exit()

        except Exception as e:
            print(f'Error requesting {cep}: {e}')

    write_json(route_json, route_json_file)
    return route_json


DF_FILE = '../data/ie_data.csv'
ADDRESS_JSON_FILE = '../data/address.json'
COORDINATE_JSON_FILE = '../data/coordinate.json'
ROUTE_JSON_FILE = '../data/route.json'

cep_list = unique_ceps(DF_FILE)

request_address(cep_list, ADDRESS_JSON_FILE)
request_coordinate(cep_list, ADDRESS_JSON_FILE, COORDINATE_JSON_FILE)
request_route(cep_list, COORDINATE_JSON_FILE, ROUTE_JSON_FILE)
