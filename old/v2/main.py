import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import analysis
import helpers
import pre_process
import process
import parameters

#############################################################################

HORIZON = 1  # Analyses the first year subjects only

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
data_csv = pre_process.entry_type(data_csv)
data_csv = pre_process.define_dropout(data_csv)
data_csv = pre_process.horizon(data_csv, HORIZON)
data_csv = pre_process.course_semester(data_csv)
data_csv = pre_process.course_attributes(data_csv, materias)
data_csv = pre_process.distancia(data_csv, google_maps_info)


# Saves the pre-processed dataframe
PP_DATA_FILE = 'pp_data.csv'
# data_csv = pd.read_csv(PP_DATA_FILE, low_memory=False).drop(columns=['Unnamed: 0'])

# analysis.double_bar_graph(data_csv, 'Distancia', 'Evadido')

data_csv.to_csv(PP_DATA_FILE)

# analysis.corr_matrix(data_csv, ['Evadido',
#                                 'Sexo',
#                                 # 'Distancia',
#                                 # 'ForaDF',
#                                 'Aprovado_1_113034',
#                                 'Reprovado_1_113034',
#                                 'Aprovado_1_118001',
#                                 'Reprovado_1_118001',
#                                 'IRA_1',
#                                 'IRA_2',
#                                 'Forma de ingresso_Vestibular',
#                                 'Forma de ingresso_Programa de Avaliação Seriada',
#                                 'Forma de ingresso_Outro',
#                                 'Forma de ingresso_Sisu-Sistema de Seleção Unificada',])


###############################################################################

# Process

X_train, X_test, y_train, y_test = process.train_test_data(data_csv)

# X_train, X_test = process.scale(X_train, X_test)

classifiers = [
    ('Floresta Aleatória', parameters.rf_model, parameters.rf_param_grid),
    ('XGBoost', parameters.xgb_model, parameters.xgb_param_grid),
    # ('Regressão Logística', parameters.lr_model, parameters.lr_param_grid),
    # ('Árvore de Decisão', parameters.dt_model, parameters.dt_param_grid),
    # ('Redes Neurais', parameters.nn_model, parameters.nn_param_grid),
    # ('SVM', parameters.svm_model, parameters.svm_param_grid),
    # ('CatBoost', parameters.cb_model, parameters.cb_param_grid),
]


for classfier in classifiers:
    process.cross_validation(classfier[0], classfier[1], classfier[2],
                             X_train, y_train, X_test, y_test)
# plt.show()
