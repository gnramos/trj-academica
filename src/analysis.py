import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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
    grouped_data = data[col].value_counts(ascending=True).reset_index() # group data by 'col'
    if sort:
        grouped_data = grouped_data.sort_values('index').reset_index() # use for sorting datas at x coordinate
    grouped_data = grouped_data.astype({'index': 'string'}) # treat as a string (sns.barplot will order if int)

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
    sns.catplot(x=attr1, y='count', hue=attr2, data=graph, kind='bar', palette='Blues')
    plt.ylabel('Quantidade')
    plt.xlabel(f'{attr1} / {attr2}')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def corr_matrix(data, attrs):
    """
    Show a correlation matrix with the attributes received.
    """
    graph = sns.heatmap(data[attrs].corr(), annot=True, cmap="Blues")
    plt.show()

    graph.figure.savefig('correlação.png', dpi=2000)

def corr_matrix_evadido(data, attrs):
    full_data(data[attrs].corr()['Evadido'])