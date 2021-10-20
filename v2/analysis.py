import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve

#############################################################################

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
    grouped_data = data[col].value_counts(ascending=True).reset_index()  # group data by 'col'
    if sort:
        grouped_data = grouped_data.sort_values('index').reset_index()  # use for sorting datas at x coordinate
    grouped_data = grouped_data.astype({'index': 'string'})  # treat as a string (sns.barplot will order if int)

    # plt.style.use('seaborn-talk')
    graph = sns.barplot(
        x='index',
        y=grouped_data[col],
        data=grouped_data,
        # palette='Blues',
        palette='mako',
    )

    # visual enhancements
    plt.ylabel('Quantidade')
    plt.xlabel(col)
    plt.xticks(rotation=90)
    plt.tight_layout()

    # show values in the graph
    add_values_above_bar(grouped_data, graph, col)

    # save and show the graph
    # graph.figure.savefig(f'{col}.png', dpi=300)
    plt.show()

def full_data(data):
    """
    Show a dataframe with more info than .head()
    """
    with pd.option_context('display.max_rows', 70, 'display.max_columns', None):
        print(data)

def double_bar_graph(data, attr1, attr2):
    """
    Show graph attr1 - attr2
    """
    graph = data[[attr1, attr2]].value_counts(ascending=True).reset_index(name='count')
    graph = graph.sort_values(attr1).reset_index()
    g = sns.catplot(x=attr1, y='count', hue=attr2, data=graph, kind='bar', legend_out = True)
    plt.ylabel('Quantidade')
    plt.xlabel(attr1)
    plt.xticks(rotation=90)
    # plt.legend()
    g.legend.set_title(attr2)
    plt.tight_layout()


    from itertools import product
    class_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
    hue_order = [False, True]
    bar_order = product(hue_order, class_order)

    spots = zip(g.ax.patches, bar_order)
    for idx, spot in enumerate(spots):
        class_total = len(data[data[attr1]==spot[1][1]])
        class_who_total = len(data[(data[attr1]==spot[1][1]) & 
                              (data[attr2]==spot[1][0])])

        if(class_total==0 or class_who_total==0):
            continue

        height = spot[0].get_height() 
        g.ax.text(spot[0].get_x(), height+3, '{:1.0f}%'.format(100*class_who_total/class_total))



    plt.show()

def corr_matrix(data, attrs):
    """
    Show a correlation matrix with the attributes received.
    """
    graph = sns.heatmap(data[attrs].corr(), annot=True, cmap='mako')
    plt.tight_layout()
    plt.show()

    # graph.figure.savefig('correlação.png', dpi=2000)

def corr_matrix_evadido(data, attrs):
    full_data(data[attrs].corr()['Evadido'])

def precision_recall_graph(name, model, X_test, y_test):
    y_prob = model.predict_proba(X_test)
    pos_probs = y_prob[:, 1]
    precision, recall, _ = precision_recall_curve(y_test, pos_probs, pos_label=1)
    plt.plot(recall, precision, marker='.', label=name)
    plt.xlabel('Sensibilidade')
    plt.ylabel('Precisão')
    plt.legend()

def roc_graph(name, model, X_test, y_test):
    y_prob = model.predict_proba(X_test)
    pos_probs = y_prob[:, 1]
    fpr, tpr, _ = roc_curve(y_test, pos_probs, pos_label=1)
    plt.plot(fpr, tpr, marker='.', label=name)
    plt.xlabel('Falso Positivo')
    plt.ylabel('Verdadeiro Positivo')
    plt.legend()

def f_importance_xgb(model):
    feature_important = model.get_booster().get_score(importance_type='weight')
    keys = list(feature_important.keys())
    values = list(feature_important.values())
    data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by = "score", ascending=False)
    data.plot(kind='barh', legend=None, xlabel='Atributos', color='mako')
    plt.tight_layout()
    plt.show()

def f_importance_rf(model, X_train):
    importances = model.feature_importances_
    forest_importances = pd.Series(importances, index=X_train.columns)
    fig, ax = plt.subplots()
    forest_importances = forest_importances.sort_values(ascending=False)[:15]
    forest_importances.plot.barh(ax=ax)
    plt.ylabel('Atributo')
    plt.tight_layout()
    plt.show()
