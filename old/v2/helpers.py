import json
import pandas as pd

def date_to_real(date):
    """
    Transform the date into a real number.
    Dates are in the format YYYY/S.
    Ex:
    2018/2 -> 2018.5
    2018/1 -> 2018.0
    2018/0 -> 2018.0
    Summer courses are processed as if they were done in the first semester of the year.
    """
    year = int(date.split('/')[0])
    semester = int(date.split('/')[1])
    return year + 0.5*(semester==2)

def read_json(file_name):
    """
    Open a json file.
    """
    with open(file_name, 'r') as outfile:
        return json.load(outfile)

def one_hot_encoding(data, columns):
    """
    Apply the one-hot encoding in the columns.
    """
    for col in columns:
        one_hot = pd.get_dummies(data[col])
        data = data.drop(col, axis = 1)
        one_hot.columns = map(lambda x: f'{col}_{x}', one_hot.columns)
        data = data.join(one_hot)
    return data
