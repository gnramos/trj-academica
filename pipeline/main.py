import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier

# import utils
import pre_process

###############################################################################

# Read Data

DATA_FILE = '../data/ie_data.csv'
data_pre = pd.read_csv(DATA_FILE, sep=';', low_memory=False)

###############################################################################

# Pre-Process data

attrs = []
data_pre = pre_process.format_data(data_pre)
data_pre = pre_process.erase_attr(data_pre)
data_pre = pre_process.public_school(data_pre, attrs)
data_pre = pre_process.credits(data_pre, attrs)
data_pre = pre_process.dropout(data_pre, attrs)
data_pre = pre_process.course(data_pre, attrs)
data_pre = pre_process.gender(data_pre, attrs)
data_pre = pre_process.quota(data_pre, attrs)
data_pre = pre_process.entry(data_pre, attrs)
# data_pre = pre_process.ira(data_pre, attrs)
data_pre = pre_process.programming_subjects(data_pre, attrs)

# Cep needs to be processed before drop_duplicates,
# otherwise it takes too long to process.
data_pre = data_pre[attrs+['cep']].drop_duplicates()
data_pre = pre_process.cep(data_pre, attrs)
data_analysis = data_pre.copy()
data_pre = data_pre.drop(columns='cep')

# Dataframe used by the algorithms
data_pre = data_pre[attrs].drop_duplicates()
data_process = data_pre.copy()

# Separate courses into different dataframes
data_course = pre_process.divide_course(data_process)

###############################################################################

# Process data


def process(data_process):
    output_attr = 'dropout'
    X = data_process.drop(columns=[output_attr])
    y = data_process[output_attr]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    model = CatBoostClassifier()
    model.fit(X_train, y_train, cat_features=['course', 'entry'], plot=True)

    predicts = model.predict(X_test)
    predicts = [x == 'True' for x in predicts]
    print('Accuracy score:', accuracy_score(y_test, predicts))
    print('Recall score:', recall_score(y_test, predicts))
    print('Precision score:', precision_score(y_test, predicts))


process(data_process)
