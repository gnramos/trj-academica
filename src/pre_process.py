import pandas as pd

import helpers

#############################################################################

def rm_not_used_attr(data):
    """
    Remove columns with information not used in the analysis.
    """
    attr = ['Quantidade de alunos', # doesn't seem to make any sense
            'Tipo de escola',       # about half of the data is missing
            'Nome disciplina']      # redundant with the discipline code
    data = data.drop(columns=attr)
    return data

def rm_students_from_other_courses(data):
    """
    Remove students that attended to other courses before their entry.
    This students have done some subjects before their entry in the course,
    making it impossible to know in what semester they attended the subject
    in relation to their entry.
    """
    students = set()
    for _, row in data.iterrows():
        entry = row['Período de ingresso']
        course = row['Semestre/Ano']
        if helpers.date_to_real(entry) > helpers.date_to_real(course):
            students.add(row['RA'])

    data = data.drop(data.loc[data['RA'].isin(students)].index)
    return data

def rm_students_convenio_andifes(data):
    """
    Remove students that attended to the courses before their entry.
    All students who entered through the convenio andifes were disconnected
    and do not have the initial disciplines accounted.
    """
    data = data.drop(data.loc[data['Forma de ingresso']=='Convênio - Andifes            '].index)
    return data

def rm_specific_data(data):
    """
    Remove data with specific problems identified.
    """
    data = rm_students_from_other_courses(data)
    data = rm_students_convenio_andifes(data)
    return data

def rm_other_courses(data, materias):
    """
    Remove courses that aren't in the materias.json
    """
    data = data.drop(data[~data['Código da disciplina'].isin(materias)].index)
    return data



def define_dropout(data):
    """
    Group together the attribute 'Forma de saída' based on the used definition of dropout.
    This function create a new attribute named 'Evadido', that is false when the student
    droupped out, and true otherwise.
    """
    attr = 'Forma de saída'

    not_dropout = ['Formatura                     ',]
    dropout = [
                'Deslig - não cumpriu condição ',
                'Repr 3 vezes na mesma disc obr',
                'Desligamento Voluntário       ',
                'Desligamento - Abandono       ',
                'Desligamento por Força de Intercãmbio',
                'Desligamento-Força de Convênio',
                'Anulação de Registro          ',
                'Desligamento Jubilamento      ',
                'Desligamento Decisão  Judicial',
                'Novo Vestibular               ',
                'Transferência                 ',
                'Vestibular p/outra Habilitação',
               ]
    erase = [
               'Aluno Ativo',
               'Falecimento                   ',
             ]

    # Erase students not used
    data.drop(data.loc[data[attr].isin(erase)].index, inplace=True)
    # Generates a new "Evadido" attribute
    data[attr] = data.apply(lambda x: x[attr] in dropout, axis=1)
    data.rename(columns={attr: 'Evadido'}, inplace=True)
    return data

def sex(data):
    """
    Assign true if feminine and false if masculine.
    """
    attr = 'Sexo'
    data[attr] = data.apply(lambda x: x[attr]=='Feminino', axis=1)
    return data

def horizon(data, horizon_years):
    """
    Remove courses that weren't attended within the horizon.
    Parameters:
        horizon_years - real number representing the horizon in years.
    """
    def beyond_horizon(row):
        """
        Compare the student's entry with the semester the course was attended,
        and check if it was attended within the horizon.
        """
        return helpers.date_to_real(row['Semestre/Ano']) >= \
               helpers.date_to_real(row['Período de ingresso']) + horizon_years

    data.drop(data[data.apply(beyond_horizon, axis=1)].index, inplace=True)
    return data

def course_semester(data):
    """
    Add a prefix to the course code, the semester the course was attended.
    Ex: 118001 -> 1_118001
    """
    def add_semester_prefix(row):
        semester = int(2*helpers.date_to_real(row['Semestre/Ano']) -
                       2*helpers.date_to_real(row['Período de ingresso'])) + 1
        return f"{semester}_{row['Código da disciplina']}"

    data['Código da disciplina'] = data.apply(add_semester_prefix, axis=1)
    return data

def course_attributes(data, materias):
    """
    Create boolean attributes for each semester_course.
    Aprovado_semester_course: 0 - Nulo
                              1 - MM/CC
                              2 - MS
                              3 - SS

    Reprovado_semester_course: 0 - Nulo
                               1 - MI
                               2 - II
                               3 - SR
    """

    def add_approved_failed_attr(data, courses):
        """
        Add the Aprovado and Reprovado attributes.
        """
        failed = {'SR': 3,
                  'II': 2,
                  'MI': 1}
        approved = {'SS': 3,
                    'MS': 2,
                    'MM': 1,
                    'CC': 1}
        for course in courses:
            data[f'Reprovado_{course}'] = data[course]
            data = data.rename(columns={course: f'Aprovado_{course}'})

        for course in courses:
            failed_attr = f'Reprovado_{course}'
            approved_attr = f'Aprovado_{course}'
            data[failed_attr] = data.apply(lambda x: failed[x[failed_attr]] if x[failed_attr] in failed else 0, axis=1)
            data[approved_attr] = data.apply(lambda x: approved[x[approved_attr]] if x[approved_attr] in approved else 0, axis=1)

        return data

    def add_approved_failed_creditos(data, courses, materias):
        """
        Add the failed and approved creditos attributes.
        """
        data['Creditos_Reprovados'] = 0
        data['Creditos_Aprovados'] = 0
        failed = ['SR', 'II', 'MI']
        approved = ['SS', 'MS', 'MI', 'CC']
        for course in courses:
            cours_code = course.split('_')[1]
            creditos = materias[cours_code]['creditos']
            data.loc[data[course].isin(failed), 'Creditos_Reprovados'] += creditos
            data.loc[data[course].isin(approved), 'Creditos_Aprovados'] += creditos

        return data


    index = [x for x in data.columns if x not in ['Menção', 'Código da disciplina', 'Semestre/Ano']]
    data = data.pivot_table(values='Menção',
                            index=index,
                            columns='Código da disciplina',
                            aggfunc='last',
                            # fill_value=3, # Not Attended
                            fill_value='NA' # Not Attended
                            ).reset_index()

    courses = [x for x in data.columns if x not in index]

    data = add_approved_failed_creditos(data, courses, materias)
    data = add_approved_failed_attr(data, courses)


    return data

def distancia(data, google_maps_info):
    """
    Use the google_maps_info.json to create a new attribute
    called 'Distancia', which tell the distance from the UnB to
    the student's home.
    Also create a new attribute called 'ForaDF', which indicates
    if the student if from outside the state (more than 50000km).
    """
    data_distance_limit = 50000
    data['Distancia'] = data_distance_limit
    data['ForaDF'] = False

    for index, row in data.iterrows():
        cep = str(row['CEP']).zfill(8)
        if cep not in google_maps_info:
            data.drop(index, inplace=True) # remove the missing cep info students
        else:
            info = google_maps_info[cep]
            if 'distance' not in info['rows'][0]['elements'][0]:
                print(f'cep = {cep}')

            dist = info['rows'][0]['elements'][0]['distance']['value']  # meters
            # time = info['rows'][0]['elements'][0]['duration']['value']  # minutes
            dist = int(dist)
            if dist > data_distance_limit:
                data.at[index, 'ForaDF'] = True
                # data.drop(index, inplace=True)
            else:
                data.at[index, 'Distancia'] = dist
    return data
