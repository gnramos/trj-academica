import matplotlib as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
import sklearn.metrics

import pre_process

# TODO: make the relative path relative to the main.py file.
DATA_FILE = '../data/ie_data.csv'
data = pd.read_csv(DATA_FILE, sep=';', low_memory=False)
# Remove leading and trailing spaces
data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Pre-Process
columns = ['cep']
data = pre_process.dropout(data, columns)
data = pre_process.public_school(data, columns)
data = pre_process.course(data, columns)
data = pre_process.gender(data, columns)
data = pre_process.quota(data, columns)
data = pre_process.ira(data, columns)
data = pre_process.programming_subjects(data, columns)

data = data[columns]
data.drop_duplicates(inplace=True)

# cep before drop_duplicates, so it doesn't take too long to process
data = pre_process.cep(data, columns)

print(data.columns)
print(data.head())

# Process
attr = 'dropout'
X = data.drop(columns=[attr])
y = data[attr]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

model = CatBoostClassifier()
# model.fit(X_train, y_train, cat_features=[2], plot=True)
model.fit(X_train, y_train, cat_features=[2])

predictions = model.predict(X_test)
predictions = [x == 'True' for x in predictions]
print("Accuracy score:", sklearn.metrics.accuracy_score(y_test, predictions))
print("Recall score:", sklearn.metrics.recall_score(y_test, predictions))
print("Precusion score:", sklearn.metrics.precision_score(y_test, predictions))
