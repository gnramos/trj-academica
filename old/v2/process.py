from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.metrics import make_scorer, fbeta_score
from sklearn.metrics import precision_recall_curve
import numpy as np

import matplotlib.pyplot as plt
import xgboost as xgb
import pandas as pd

import analysis

def fbeta(precision, recall, beta):
    return (1+beta**2) * (precision*recall) / (precision*beta**2 + recall)

def metrics(X, y, model, BETA):
    """
    Choose the best threshold for maximizing the Fbeta-Score
    and calculate the accuracy, precision, recall and Fbeta-Score.
    """
    y_prob = model.predict_proba(X)[:, 1]
    precision_list, recall_list, thresholds = precision_recall_curve(y, y_prob, pos_label=1)

    best_id = np.argmax(fbeta(precision_list, recall_list, BETA))
    threshold = thresholds[best_id]
    y_pred = [y>=threshold for y in y_prob]
    accuracy = accuracy_score(y.values, y_pred)
    precision, recall, fscore, _ = precision_recall_fscore_support(y.values, y_pred,
                                                                   beta=BETA, average='binary')
    return accuracy, precision, recall, fscore

def cross_validation(name, model, param, X_train, y_train, X_test, y_test):
    """
    Train the model using cross-validation 5-fold,
    and show the accuracy, precision, recall and F-score
    for both the train and test data.
    """
    BETA = 1.5
    fbeta = make_scorer(fbeta_score, beta=BETA)
    gs = GridSearchCV(model, param, cv=5, scoring=fbeta)
    gs.fit(X_train, y_train)

    print(f'{name} with GridSearch:')
    print(f'Melhores parêmtros: {gs.best_params_}')
    print('(Acurácia, Precisão, Sensibilidade, FScore)')

    accuracy, precision, recall, fscore = metrics(X_train, y_train, gs, BETA)
    print('Treino:')
    print(f'({100*accuracy:.2f}%, {100*precision:.2f}%, {100*recall:.2f}%, {100*fscore:.2f}%)')


    accuracy, precision, recall, fscore = metrics(X_test, y_test, gs, BETA)
    print('Teste:')
    print(f'({100*accuracy:.2f}%, {100*precision:.2f}%, {100*recall:.2f}%, {100*fscore:.2f}%)')

    analysis.precision_recall_graph(name, gs, X_test, y_test)

    best_model = gs.best_estimator_
    if name == 'XGBoost':
        analysis.f_importance_xgb(best_model)
    elif name == 'Floresta Aleatória':
        analysis.f_importance_rf(best_model, X_train)

def scale(X_train, X_test):
    """
    Scale the train and test data.
    """
    scaler = StandardScaler()
    scaler.fit(X_train.values)
    X_train = scaler.transform(X_train.values)
    X_test = scaler.transform(X_test.values)
    return X_train, X_test


def train_test_data(data):
    """
    Generate the train and test data
    """
    X = data.drop(columns=['Evadido', 'CEP', 'RA',
                           # 'Sexo',
                           # 'Forma de ingresso',
                           # 'Distancia', 'ForaDF',
                           'Período de ingresso', 'Período de saída'])
    y = data['Evadido']
    return train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
