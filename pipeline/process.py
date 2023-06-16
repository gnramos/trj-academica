# Process Module

from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.metrics import precision_recall_curve
import numpy as np


def fbeta(precision, recall, BETA):
    return (1+BETA**2) * (precision*recall) / (precision*BETA**2 + recall)


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


def log_metrics(model, X_train, y_train, X_test, y_test, course):
    """
    Log the accuracy, precision, recall and fscore
    for both the train and test data.
    """
    BETA = 1.2

    threshold = best_threshold(model, X_train, y_train, BETA)

    with open('/home/raphaela/Documentos/unb/pibic/trj-academica-dados-novos/results/README.md', 'a+') as f:

        accuracy, precision, recall, fscore = metrics(
            X_train, y_train, model, BETA, threshold
        )

        f.write(f'## {course}\n')

        f.write('Treino:\n')
        f.write(f'*   Accuracy = {100*accuracy:.2f}%\n')
        f.write(f'*   Precision = {100*precision:.2f}%\n')
        f.write(f'*   Recall = {100*recall:.2f}%\n')
        f.write(f'*   FScore = {100*fscore:.2f}%\n')
        f.write('\n')

        accuracy, precision, recall, fscore = metrics(
            X_test, y_test, model, BETA, threshold
        )
        f.write('Teste:\n')
        f.write(f'*   Accuracy = {100*accuracy:.2f}%\n')
        f.write(f'*   Precision = {100*precision:.2f}%\n')
        f.write(f'*   Recall = {100*recall:.2f}%\n')
        f.write(f'*   FScore = {100*fscore:.2f}%\n')
        f.write('\n')


def log_params(params):
    with open('/home/raphaela/Documentos/unb/pibic/trj-academica-dados-novos/results/README.md', 'a+') as f:

        f.write('Parametros:\n')
        for p, v in params.items():
            f.write(f'*   {p} = {v}\n')
        f.write('\n')
