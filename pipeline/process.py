# Process Module

from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.metrics import precision_recall_curve
import numpy as np


def fbeta(precision, recall, beta):
    return (1+beta**2) * (precision*recall) / (precision*beta**2 + recall)


def metrics(X, y, model, BETA, threshold):
    """Calculate the accuracy, precision, recall and Fbeta-Score."""
    y_prob = model.predict_proba(X)[:, 1]
    y_pred = [y >= threshold for y in y_prob]
    accuracy = accuracy_score(y.values, y_pred)
    precision, recall, fscore, _ = precision_recall_fscore_support(
        y.values, y_pred, beta=BETA, average='binary'
    )
    return accuracy, precision, recall, fscore


def best_threshold(model, X, y, BETA):
    """Choose the best threshold for maximizing the Fbeta-Score."""
    y_prob = model.predict_proba(X)[:, 1]
    precision_list, recall_list, thresholds = precision_recall_curve(
        y, y_prob, pos_label=1
    )
    best_id = np.argmax(fbeta(precision_list, recall_list, BETA))
    threshold = thresholds[best_id]
    return threshold


def show_metrics(model, X_train, y_train, X_test, y_test):
    """
    Show the accuracy, precision, recall and F-score
    for both the train and test data.
    """
    BETA = 1.5

    threshold = best_threshold(model, X_train, y_train, BETA)

    accuracy, precision, recall, fscore = metrics(
        X_train, y_train, model, BETA, threshold
    )
    print('Treino:')
    print(f'Accuracy = {100*accuracy:.2f}%')
    print(f'Precision = {100*precision:.2f}%')
    print(f'Recall = {100*recall:.2f}%')
    print(f'FScore = {100*fscore:.2f}%')

    accuracy, precision, recall, fscore = metrics(
        X_test, y_test, model, BETA, threshold
    )
    print('Teste:')
    print(f'Accuracy = {100*accuracy:.2f}%')
    print(f'Precision = {100*precision:.2f}%')
    print(f'Recall = {100*recall:.2f}%')
    print(f'FScore = {100*fscore:.2f}%')
