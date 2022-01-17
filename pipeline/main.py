import matplotlib as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os

import pre_process

DATA_FILE = '../data/ie_data.csv'
data = pd.read_csv(DATA_FILE, sep=';', low_memory=False)
# Remove leading and trailing spaces
data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Pre-Process
columns = ['cep']
data = pre_process.public_school(data, columns)
data = pre_process.dropout(data, columns)
data = pre_process.course(data, columns)
data = pre_process.gender(data, columns)
data = pre_process.quota(data, columns)
data = pre_process.ira(data, columns)

data = data[columns]
data.drop_duplicates(inplace=True)

data = pre_process.cep(data, columns)

print(data.columns)
print(data.head())
