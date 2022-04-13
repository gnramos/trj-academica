# Pre Process Module

from hashlib import new
from types import new_class
import pandas as pd
import unicodedata
import utils


def erase_attr(data):
    """Erase unused attributes."""
    attrs = [
        'sistema_origem',
        'id_pessoa',
        'ira',
        'endereco',
        'estado_nascimento',
        'raca',
        'chamada_ingressou_unb',
        'ano_ensino_medio',
        'modalidade_disciplina',
        'media_semestre_aluno',
        'min_cred_para_formatura',
        'total_creditos_cursados_aluno',
        'codigo_disciplina',
        'media_semestre_aluno',
    ]
    data = data.drop(columns=attrs)
    return data


def erase_internal_transfer_students(data):
    """
    Remove students that attended to other courses before their entry.
    Those students have done some subjects before their entry in the course,
    making it impossible to know in what semester they attended the subject
    in relation to their entry.
    """
    students = set()
    for _, row in data.iterrows():
        entry = row['periodo_ingresso_curso']
        subject = row['periodo_cursou_disciplina']
        if utils.date_to_real(entry) > utils.date_to_real(subject):
            students.add(row['aluno'])

    data = data.drop(data.loc[data['aluno'].isin(students)].index)
    return data


def format_data(data):
    """
    Remove leading and trailing spaces, and lowers all string elements,
    accents from the subjects names, and replaces spaces with underscores.
    """
    def strip_accents(value):
        return ''.join(
            c for c in unicodedata.normalize('NFD', value)
            if unicodedata.category(c) != 'Mn'
        )

    def format(value):
        return value.str.strip().str.lower().str.replace(' ', '_')

    # Leading/trailing spaces, lower characters and underscores.
    data = data.apply(lambda x: format(x) if x.dtype == 'object' else x)
    data.columns = format(data.columns)

    # Accents in subjects.
    attr = 'nome_disciplina'
    data[attr] = data[attr].apply(lambda x: strip_accents(x))

    return data


def gender(data, attrs):
    """Tranform the gender attribute in a boolean and rename it."""
    attr = 'genero'
    newattr = 'female'
    data[attr] = data.apply(lambda x: x[attr] == 'f', axis=1)
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def quota(data, attrs, attrs_cat):
    """Tranform the quota attribute in a boolean and rename it."""
    attr = 'sistema_cotas'
    newattr = 'quota'
    data[attr] = data.apply(lambda x: x[attr] == 'sim', axis=1)
    data = data.rename({attr: newattr}, axis=1)
    attrs.append(newattr)

    attr = 'cota'
    newattr = 'quota_type'
    data[attr] = data[attr].fillna('universal')
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    attrs_cat.append(newattr)

    return data


def public_school(data, attrs):
    """Tranform the school type attribute in a boolean and rename it."""
    attr = 'escola'
    newattr = 'public_school'
    data[attr] = data.apply(lambda x: x[attr] == 'publica', axis=1)
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def entry(data, attrs, attrs_cat):
    """
    Choose the four most frequent values for the entry form attribute,
    aggregate the others, and rename the attribute.
    """
    attr = 'forma_ingresso_unb'
    newattr = 'entry'

    entry_types = [
        'vestibular',
        'programa_de_avaliação seriada',
        'transferência_obrigatória',
        'sisu-sistema_de_seleção unificada',
    ]

    data[attr] = data.apply(
        lambda x: x[attr] if x[attr] in entry_types else 'outro', axis=1
    )
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    attrs_cat.append(newattr)
    return data


def age(data, attrs):
    """
    Generate an attribute informing the age of the student at entry,
    using the birth date attribute.
    """
    attr = 'nascimento'
    newattr = 'age'

    def birth_to_age(x):
        return (
            int(x['periodo_ingresso_unb'] // 10) - int(x[attr].split("/")[2])
        )

    data[attr] = data.apply(birth_to_age, axis=1)
    data.drop(data.loc[data[attr] <= 0].index, inplace=True)

    data = data.rename({attr: newattr}, axis=1)
    attrs.append(newattr)
    return data


def course(data, attrs):
    """Group and rename the courses names."""
    attr = 'curso'
    newattr = 'course'

    data[attr] = data[attr].replace({
        "engenharia_mecatrônica_-_" +
        "controle_e_automação": "engenharia_mecatrônica",
        "controle_e_automação": "engenharia_mecatrônica",

        "informática": "computação",

        "matematica_-_licenciatura noturno": "matemática",
        "matematica_-_licenciatura diurno": "matemática",
        "matematica_-_bacharelado diurno": "matemática"
    })
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def cic_courses(data):
    """Keep only courses from the computer science departament (CIC-UNB)"""
    cic_courses = [
        'ciência_da_computação',
        'computação',
        'engenharia_de_computação',
        'engenharia_mecatrônica'
    ]
    attr = 'course'
    data.drop(data.loc[~data[attr].isin(cic_courses)].index, inplace=True)
    return data


def dataframe_specific_adjustments(data):
    # Consider 'computacao basica' & 'algoritmos e programacao de computadores'
    # to be the same subject by renaming them.
    attr = 'nome_disciplina'
    data[attr] = data[attr].replace({
        "computacao_basica": "algoritmos_e_programacao_de_computadores",
    })
    return data


def remove_anomalies(data):
    """
    Remove students with more than 60 credits in the first semester
    (probably caused by a system problem).
    """
    attr = '1_approved_credits'
    data.drop(data.loc[data[attr] > 60].index, inplace=True)
    return data


def time_frame(data, year_range):
    """Remove students with entry time outside year_range."""
    attr = 'periodo_ingresso_curso'
    data.drop(data.loc[data[attr] // 10 < year_range[0]].index, inplace=True)
    data.drop(data.loc[data[attr] // 10 > year_range[1]].index, inplace=True)
    return data


def dropout(data, attrs):
    """Transform the way out attribute into a boolean dropout attribute."""
    attr = 'forma_saida_curso'
    newattr = 'dropout'

    erase = ['falecimento', 'ativo']
    not_dropout = ['formatura', 'concluído']

    data.drop(data.loc[data[attr].isin(erase)].index, inplace=True)
    data[attr] = data.apply(lambda x: x[attr] not in not_dropout, axis=1)
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def one_hot_encoding(data, columns, attrs, attrs_cat):
    """Apply the one-hot encoding in the columns."""
    for col in columns:
        attrs.remove(col)
        attrs_cat.remove(col)
        one_hot = pd.get_dummies(data[col])
        data = data.drop(col, axis=1)
        one_hot.columns = map(lambda x: f'{col}_{x}', one_hot.columns)
        data = data.join(one_hot)
        attrs.extend(one_hot.columns)
    return data


def add_semester_prefix(data):
    """
    Add a prefix to the subject name, informing the semester it was
    attended.
    Ex: calculo 1 -> 1_calculo 1
    """
    def add_semester_prefix(row):
        semester = 1 + int(
            2 * utils.date_to_real(row['periodo_cursou_disciplina']) -
            2 * utils.date_to_real(row['periodo_ingresso_curso'])
        )
        return f"{semester}_{row['nome_disciplina']}"

    data['nome_disciplina'] = data.apply(add_semester_prefix, axis=1)
    return data


def subject_credits(data):
    """Generate a dict with credits information for every subject."""
    credits_dict = dict()
    data_subjects = data[['nome_disciplina', 'creditos_disciplina']].copy()
    data_subjects = data_subjects.drop_duplicates()

    for _, row in data.iterrows():
        credits_dict[row['nome_disciplina']] = row['creditos_disciplina']

    return credits_dict


def beyond_horizon(data, horizon):
    """
    Compare the student's entry with the semester the subject was attended,
    and remove it if it was attended beyond the horizon.
    """
    def hor(row):
        return (
            utils.date_to_real(row['periodo_cursou_disciplina']) -
            utils.date_to_real(row['periodo_ingresso_curso']) >= horizon
        )
    data.drop(data[data.apply(hor, axis=1)].index, inplace=True)
    return data


def subjects(data, attrs, horizon, credits_dict):
    """
    Generate an attribute for every subject, and for every semester,
    informing the student's grade (mention) numerically.
    It considers at most 20 of the most frequent
    subjects/semester from the first year.
    """

    def credits_attr(data, subjects, attrs, credits_dict, horizon):
        """
        Add the quantity of credits failed and approved per semester
        as attributes.
        """
        for semester in range(1, 2*horizon+1):
            attrs.append(f'{semester}_failed_credits')
            attrs.append(f'{semester}_approved_credits')
            data[f'{semester}_failed_credits'] = 0
            data[f'{semester}_approved_credits'] = 0

        failed = ['sr', 'ii', 'mi', 'tr']
        approved = ['ss', 'ms', 'mm', 'cc']

        for sub_attr in subjects:
            semester, subject = sub_attr.split('_', 1)
            credits = credits_dict[subject]
            data.loc[data[sub_attr].isin(failed),
                     f'{semester}_failed_credits'] += credits
            data.loc[data[sub_attr].isin(approved),
                     f'{semester}_approved_credits'] += credits

        return data

    def ira_attr(data, subjects, attrs, credits_dict, horizon):
        """Add IRA attribute per semester."""
        grades = {'ss': 5, 'ms': 4, 'mm': 3, 'mi': 2, 'ii': 1, 'sr': 0}

        # Initialize the attributes.
        for semester in range(1, 2*horizon+1):
            attrs.append(f'{semester}_ira')
            data[f'{semester}_ira'] = 0
            data[f'{semester}_total'] = 0  # Accumulate total credits.

        for sub_attr in subjects:
            semester, subject = sub_attr.split('_', 1)
            credits = credits_dict[subject]
            for sem in range(int(semester), 2*horizon+1):
                # Take into account for every semester before it.
                attr_ira = f'{sem}_ira'
                attr_total = f'{sem}_total'
                data[attr_ira] = data.apply(
                    lambda x: (
                        x[attr_ira] + credits*grades[x[sub_attr]]
                        if x[sub_attr] in grades else x[attr_ira]
                    ), axis=1
                )
                data[attr_total] = data.apply(
                    lambda x: (
                        x[attr_total] + credits
                        if x[sub_attr] in grades else x[attr_total]
                    ), axis=1
                )

        # Calculate the ira.
        for semester in range(1, 2*horizon+1):
            attr_ira = f'{semester}_ira'
            attr_total = f'{semester}_total'
            data[attr_ira] = data.apply(
                lambda x: (
                    x[attr_ira] / x[attr_total] if x[attr_total] > 0 else 0
                ), axis=1
            )

        return data

    def numerical_grades(data, subjects_freq):
        """"Transform grades (mentions) into numbers."""
        grades = {
            'sr': -3,
            'ii': -2,
            'mi': -1,
            'cc': 1,
            'mm': 1,
            'ms': 2,
            'ss': 3
        }
        for sub in subjects_freq:
            data[sub] = data.apply(
                lambda x: grades[x[sub]] if x[sub] in grades else 0, axis=1
            )
        return data

    attr_subject = 'nome_disciplina'
    attr_grade = 'mencao_disciplina'

    # Find the "n_sub" most frequent subjects/semester.
    n_sub = 25
    subjects_freq = data[attr_subject].value_counts()[0:n_sub].index.to_list()

    # Calculate IRA only the "n_sub" most frequents subjects.
    ira_subjects = data[attr_subject].value_counts()[0:n_sub].index.to_list()
    # ira_subjects = data[attr_subject].value_counts().index.to_list()

    # Remove attributes that are different for a single student,
    # so we can use pivot_table.
    out = [
        'periodo_cursou_disciplina',
        'creditos_no_periodo',
        'creditos_aprovado_periodo',
        'creditos_disciplina',
    ]
    data = data.drop(columns=out)

    index = data.columns.difference([attr_grade, attr_subject]).tolist()

    # Transform each subject into an attribute.
    data = data.pivot_table(
        values=attr_grade,
        index=index,
        columns=attr_subject,
        aggfunc='first',
        fill_value='na',  # Not Attended
    ).reset_index()
    data.index.name = None

    subjects_attr = data.columns.difference(index).tolist()

    data = credits_attr(data, subjects_attr, attrs, credits_dict, horizon)
    data = ira_attr(data, ira_subjects, attrs, credits_dict, horizon)

    # TODO implement for a variable horizon value
    # Prefix maximum the subject's grade.

    # Keep only the most frequent subjects/semester.
    subjects_rm = [sub for sub in subjects_attr if sub not in subjects_freq]
    data = data.drop(columns=subjects_rm)

    data = numerical_grades(data, subjects_freq)

    for sub_attr in subjects_freq:
        if sub_attr.startswith('2'):
            sub_attr_last = f'1{sub_attr[1:]}'
            if sub_attr_last in data.columns:
                data[sub_attr] = data.apply(
                    lambda x: max(x[sub_attr], x[sub_attr_last]), axis=1)

    attrs.extend(subjects_freq)

    return data


def cep(data, attrs):
    """
    Transform the cep into the distance from the student's home
    to the University of Brasília. Uses the data requested using the
    cep_gen.py script. It removes students from out of the region (DF).
    """

    attr = 'cep'
    newattr = 'distance'

    data.dropna(subset=[attr])

    route_json = utils.read_json('../data/route.json')
    address_json = utils.read_json('../data/address.json')
    # coordinate_json = utils.read_json('../data/coordinate.json')
    data[attr] = data.apply(lambda x: utils.format_cep(x[attr]), axis=1)

    cep_unb = '70910900'
    data.drop(data[data[attr] == cep_unb].index, inplace=True)

    data[newattr] = 0

    for index, row in data.iterrows():
        cep = str(row[attr])
        if (cep not in route_json) or (route_json[cep]['status'] != 'OK'):
            # remove students with missing cep
            data.drop(index, inplace=True)
        else:
            info = route_json[cep]

            dist = info['distance']['value']  # meters
            # time = info['duration']['value']  # minutes
            dist = int(dist)
            if address_json[cep]['uf'] != 'DF':
                # remove students from out of DF
                data.drop(index, inplace=True)
            else:
                data.at[index, newattr] = dist

    attrs.append(newattr)
    return data


def divide_course(data, attrs, attrs_cat):
    """
    Return one dictionary with subsets of the data, separated by course,
    and other two dicts, informing the attributes of each subset.
    """
    attr = 'course'
    attrs_copy = attrs.copy()
    attrs_copy.remove(attr)  # Remove course attribute

    data_course = {}
    attrs_course = {}
    attrs_cat_course = {}

    for course in data[attr].unique():
        data_course[course] = data.copy()[data[attr] == course]
        attrs_course[course] = attrs_copy.copy()
        attrs_cat_course[course] = attrs_cat.copy()

    return data_course, attrs_course, attrs_cat_course
