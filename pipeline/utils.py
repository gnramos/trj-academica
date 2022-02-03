# Utils Module

import json
import os
import re
import matplotlib.pyplot as plt


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


def format_cep(cep):
    """Remove the non-numeric characters and add trailing zeros in cep."""
    return re.sub('[^0-9]', '', str(cep)).ljust(8, '0')


def plot_coordinates(data, title):
    x = []
    y = []
    c = []
    coordinate_json = read_json('../data/coordinate.json')
    attr = 'cep'

    for index, row in data.iterrows():
        cep = str(row[attr])
        info = coordinate_json[cep]
        if info['lat'] < -17:
            data.drop(index, inplace=True)
            continue
        x.append(info['lat'])
        y.append(-info['lng'])
        c.append('red' if row['dropout'] else 'blue')

    plt.figure(figsize=(10, 10))
    plt.title(title)
    plt.scatter(x, y, c=c, alpha=0.2)
    plt.show()
