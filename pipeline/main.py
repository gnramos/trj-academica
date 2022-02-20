from defer import inline_callbacks
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import sklearn.metrics
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier

import pre_process
import utils


import pre_process

DATA_FILE = '/home/tiago/git/trj-academica/data/ie_data.csv'
data_0 = pd.read_csv(DATA_FILE, sep=';', low_memory=False)

# Pre-Process
columns = ['cep']
data_0 = pre_process.format_data(data_0)
data_0 = pre_process.public_school(data_0, columns)
data_0 = pre_process.credits(data_0, columns)
data_0 = pre_process.dropout(data_0, columns)
data_0 = pre_process.course(data_0, columns)
data_0 = pre_process.gender(data_0, columns)
data_0 = pre_process.quota(data_0, columns)
data_0 = pre_process.entry(data_0, columns)

data_course = pre_process.divide_course(data_0)
meca = data_course['engenharia mecatrônica']
meca = pre_process.subjects(meca, columns)
data_1 = meca.copy()[columns].drop_duplicates()
# data_1 = pre_process.cep(data_1, columns)
