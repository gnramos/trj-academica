import numpy as np
import xgboost as xgb
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from catboost import CatBoostClassifier
from sklearn.svm import SVC


# Models

# RANDOM FOREST
rf_model = RandomForestClassifier()
rf_param_grid = {
    'criterion': ['gini', 'entropy'],
    # 'n_estimators': range(10,200,20),
    'n_estimators': [25, 50, 75, 100],
    'max_features': ['auto', 'sqrt'],
    'max_depth': [4, 5, 7],
}

###############################################################################

# XGBOOST
xgb_model = xgb.XGBClassifier(objective='binary:logistic',
                              eval_metric='error',
                              use_label_encoder=False)
xgb_param_grid = {
    # 'n_estimators': [100, 200],
    'min_child_weight': [1, 5, 10],
    'n_estimators': [20, 25, 35],
    'max_depth': [2, 6, 10],
}

###############################################################################

# LOGISTIC REGRESSION
lr_model = LogisticRegression(max_iter=2500)
lr_param_grid = {
    'solver': ['liblinear', 'lbfgs'],
    # 'C': np.logspace(-2, 4, 10)
}

###############################################################################

# DECISION TREE
dt_model = tree.DecisionTreeClassifier()
dt_param_grid = {
    'max_depth': [10, 25, 50, 100],
    # 'max_features': ['sqrt', 'log2', None],
    'criterion': ['gini', 'entropy'],
    'splitter': ['best', 'random'],
    'min_samples_split': np.linspace(0.1, 1.0, 10, endpoint=True)
}

###############################################################################

# NEURAL NETWORK
nn_model = MLPClassifier()
nn_param_grid = {
    'max_iter': [10000],
    'solver': ['lbfgs'],
    'activation': ['identity', 'logistic', 'tanh', 'relu'],
}

###############################################################################

# SVM
svm_model = SVC(probability=True)
svm_param_grid = {
    'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
}

###############################################################################

# CATBOOST
cb_model = CatBoostClassifier(silent=True)
cb_param_grid = {}
