# Utils Module

import json
import os
import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve


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


def date_to_real(date):
    """
    Transform the date into a real number.
    Dates are in the format YYYYS.
    Ex:
    20182 -> 2018.5
    20181 -> 2018.0
    20180 -> 2018.0
    Summer courses are processed as if they were done
    in the first semester of the year.
    """
    year = date // 10
    semester = date % 10
    return year + 0.5 * (semester == 2)


def plot_feature_importance(importance, names, model_type):
    plt.style.use('ggplot')
    data = {
        'feature_names': np.array(names),
        'feature_importance': np.array(importance)
    }
    fi_df = pd.DataFrame(data)
    fi_df.sort_values(by=['feature_importance'], ascending=False, inplace=True)
    plt.figure(figsize=(10, 8))
    sns.barplot(x=fi_df['feature_importance'], y=fi_df['feature_names'])
    plt.title(model_type + 'Feature Importance')
    plt.xlabel('Feature Importance')
    plt.ylabel('Feature Name')
    plt.show()


def plot_coordinates(data, title):
    x = []
    y = []
    c = []
    coordinate_json = read_json('../data/coordinate.json')
    attr = 'cep'

    for index, row in data.iterrows():
        cep = str(row[attr])
        info = coordinate_json[cep]
        if info['lat'] < -17 or info['lat'] > -15.5:
            data.drop(index, inplace=True)
            continue
        x.append(info['lat'])
        y.append(-info['lng'])
        c.append('red' if row['dropout'] else 'blue')

    plt.figure(figsize=(30, 40))
    plt.title(title)
    plt.scatter(x, y, c=c, alpha=0.2)
    # plt.savefig(f'img/{title}_plot.pdf')
    plt.show()


def plot_coordinates_density(data, title):

    import scipy.stats
    xi = []
    yi = []
    ci = []

    coordinate_json = read_json('../data/coordinate.json')
    attr = 'cep'

    for index, row in data.iterrows():
        cep = str(row[attr])
        info = coordinate_json[cep]
        if info['lat'] < -17 or info['lat'] > -15.5:
            data.drop(index, inplace=True)
            continue
        if(row['dropout']):
            xi.append(info['lat'])
            yi.append(-info['lng'])
        # ci.append('red' if row['dropout'] else 'blue')

    x = np.array(xi)
    y = np.array(yi)
    # c = np.array(ci)

    plt.figure(figsize=(30, 40))
    plt.title(title)

    nbins = 1000
    k = scipy.stats.gaussian_kde([x, y], bw_method=0.05)
    xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))

    # Make the plot
    plt.pcolormesh(
        xi, yi, zi.reshape(xi.shape),
        shading='auto', cmap=plt.cm.seismic
    )
    plt.colorbar()

    # plt.savefig(f'img/{title}.png')
    plt.show()


def precision_recall_graph(model, X_test, y_test):
    y_prob = model.predict_proba(X_test)
    pos_probs = y_prob[:, 1]
    precision, recall, _ = precision_recall_curve(
        y_test, pos_probs, pos_label=1
    )
    plt.plot(recall, precision, marker='.')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend()
    plt.show()


def bar_freq(data, col, sort=False):
    """
    Show a bar graph with frequencies of a specific attribute.
    Parameters:
        - col: attribute analised
        - data: dataframe
        - sort: sort frequencies by their x coordinate value
    """
    def add_values_above_bar(grouped_data, graph, col):
        """
        Show values above the bars of the graph.
        """
        for _, row in grouped_data.iterrows():
            graph.text(row.name, row[col], round(row[col], 2),
                       color='black', ha="center", fontsize=12)

    # Saves a graph with occurrence of the 'col' attribute
    grouped_data = data[col].value_counts(ascending=True).reset_index()
    if sort:
        grouped_data = grouped_data.sort_values('index').reset_index()
    # treat as a string (sns.barplot will order if int)
    grouped_data = grouped_data.astype({'index': 'string'})

    plt.style.use('seaborn-talk')
    graph = sns.barplot(
        x='index',
        y=grouped_data[col],
        data=grouped_data,
        palette='Blues',
        # palette='mako',
    )

    # visual enhancements
    plt.ylabel('Quantidade')
    plt.xlabel(col)
    plt.xticks(rotation=90)
    # plt.tight_layout()

    # show values in the graph
    add_values_above_bar(grouped_data, graph, col)

    # save and show the graph
    # graph.figure.savefig(f'{col}.png', dpi=300)
    plt.savefig(
        f'graphs/{col}.png', dpi=200, bbox_inches='tight', facecolor='#ffffff'
    )
    plt.show()
