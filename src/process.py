import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score, recall_score, precision_score

import pre_process
import analysis
import helpers

# dtype={'RA': int,
#        'Sexo': str,
#        'Tipo de escola': str,
#        'CEP': int,
#        'Forma de ingresso': str,
#        'Período de ingresso': str,
#        'Forma de saída': str,
#        'Período de saída': str,
#        'Semestre/Ano': str,
#        'Código da disciplina': str,
#        'Nome disciplina': str,
#        'Menção': str,
#        'Quantidade de alunos': str,
#       }

#############################################################################

HORIZON = 1 # Analyses the first year subjects only

DATA_FRAME_FILE = 'meca.csv'
GOOGLE_MAPS_FILE = 'google_maps_info.json'
MATERIAS_FILE = 'materias.json'

data_csv = pd.read_csv(DATA_FRAME_FILE, low_memory=False)
google_maps_info = helpers.read_json(GOOGLE_MAPS_FILE)
materias = helpers.read_json(MATERIAS_FILE)


# Pre-Process

data_csv = pre_process.rm_not_used_attr(data_csv)
data_csv = pre_process.rm_specific_data(data_csv)
data_csv = pre_process.rm_other_courses(data_csv, materias)

data_csv = pre_process.sex(data_csv)
data_csv = pre_process.define_dropout(data_csv)
data_csv = pre_process.horizon(data_csv, HORIZON)
data_csv = pre_process.course_semester(data_csv)
data_csv = pre_process.course_attributes(data_csv, materias)
data_csv = pre_process.distancia(data_csv, google_maps_info)


# Saves the pre-processed dataframe
data_csv.to_csv('teste.csv')

#####################################################################################

# Process will be a separete module soon

X = data_csv.drop(columns=['Evadido', 'Forma de ingresso', 'CEP', 'Sexo',
                           'Período de ingresso', 'Período de saída'])
y = data_csv['Evadido']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)


def scale(X_train, X_test):
    """
    Scale the train and test data.
    """
    scaler = StandardScaler()
    scaler.fit(X_train.values)
    X_train = scaler.transform(X_train.values)
    X_test = scaler.transform(X_test.values)

    return X_train, X_test

X_train, X_test = scale(X_train, X_test)



def cross_validation(model, param, name):
    """
    Train the model using cross-validation 10-fold,
    and show the accuracy, recall and precision
    for both the train and test data.
    """
    gs = GridSearchCV(model, param, cv=10, scoring='recall')
    gs.fit(X_train, y_train)

    y_pred_train = gs.predict(X_train)
    recall_train = recall_score(y_train.values, y_pred_train)
    precision_train = precision_score(y_train.values, y_pred_train)
    accuracy_train = accuracy_score(y_train.values, y_pred_train)

    y_pred_test = gs.predict(X_test)
    recall_test = recall_score(y_test.values, y_pred_test)
    precision_test = precision_score(y_test.values, y_pred_test)
    accuracy_test = accuracy_score(y_test.values, y_pred_test)

    print(f'{name} with GridSearch:')
    print('(Acurácia, Precisão, Sensibilidade)')
    print('Treino:')
    print(f'({100*accuracy_train:.2f}%, {100*precision_train:.2f}%, {100*recall_train:.2f}%)')
    print('Teste:')
    print(f'({100*accuracy_test:.2f}%, {100*precision_test:.2f}%, {100*recall_test:.2f}%)\n')




# RANDOM FOREST
rf_param_grid = {
    # 'criterion': ['gini', 'entropy'],
    # 'n_estimators': [5,10,50,100,200],
    # 'max_features': ['auto', 'sqrt']
}
# XGBOOST
xgbc_param_grid = {
    # 'n_estimators': [400],
    # 'max_depth': [20],
}
# LOGISTIC REGRESSION
lr_param_grid = {
    # 'solver': ['liblinear', 'lbfgs'],
    # 'C': np.logspace(-2, 4, 10)
}
# DECISION TREE
dt_param_grid = {
    # 'criterion': ['gini', 'entropy'],
    # 'splitter': ['best', 'random'],
    # 'min_samples_split': np.linspace(0.1, 1.0, 10, endpoint=True)
}


classifiers = [
    ('Random Forest', RandomForestClassifier(), rf_param_grid),
    ('XGBoost', xgb.XGBClassifier(objective='binary:logistic',
                                  eval_metric='error',
                                  use_label_encoder=False), xgbc_param_grid),
    ('Logistic Regression', LogisticRegression(max_iter=2500), lr_param_grid),
    ('Decision Tree', tree.DecisionTreeClassifier(), dt_param_grid)
]


for classfier in classifiers:
    cross_validation(classfier[1], classfier[2], classfier[0])
