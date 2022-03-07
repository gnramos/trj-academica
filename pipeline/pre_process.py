# Pre Process Module

import unicodedata
import utils


def erase_attr(data):
    """Erase unused attributes."""
    attrs = [
        'sistema_origem',
        'id_pessoa',
        # 'ira',
        'endereco',
        'estado_nascimento',
        'cota',
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


def erase_interal_transfer_students(data):
    """
    Remove students that attended to other courses before their entry.
    Those students have done some subjects before their entry in the course,
    making it impossible to know in what semester they attended the subject
    in relation to their entry.
    """
    students = set()
    for _, row in data.iterrows():
        entry = row['periodo_ingresso_curso']
        course = row['periodo_cursou_disciplina']
        if utils.date_to_real(entry) > utils.date_to_real(course):
            students.add(row['aluno'])

    data = data.drop(data.loc[data['aluno'].isin(students)].index)
    return data


def format_data(data):
    """
    Remove leading and trailing spaces, and lowers all string elements.
    Also removes accents from the subjects names.
    """
    def strip_accents(s):
        return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
        )

    def format(value):
        return value.str.strip().str.lower()

    data = data.apply(lambda x: format(x) if x.dtype == 'object' else x)
    data.columns = format(data.columns)

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


def quota(data, attrs):
    """Tranform the quota attribute in a boolean and rename it."""
    attr = 'sistema_cotas'
    newattr = 'quota'
    data[attr] = data.apply(lambda x: x[attr] == 'sim', axis=1)
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def public_school(data, attrs):
    """Tranform the school type attribute in a boolean and rename it."""
    attr = 'escola'
    newattr = 'public_school'
    data[attr] = data.apply(lambda x: x[attr] == 'publica', axis=1)
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def entry(data, attrs):
    """
    Choose the four most frequent values for the entry form attribute,
    aggregate the others, and rename the attribute.
    """
    attr = 'forma_ingresso_unb'
    newattr = 'entry'

    entry_types = [
        'vestibular',
        'programa de avaliação seriada',
        'transferência obrigatória',
        'sisu-sistema de seleção unificada',
    ]

    data[attr] = data.apply(
        lambda x: x[attr] if x[attr] in entry_types else 'outro', axis=1
    )
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def course(data, attrs):
    """Group and rename the courses names."""
    attr = 'curso'
    newattr = 'course'

    data[attr] = data[attr].replace({
        "engenharia mecatrônica - " +
        "controle e automação": "engenharia mecatrônica",
        "controle e automação": "engenharia mecatrônica",

        "informática": "computação",

        "matematica - licenciatura noturno": "matemática",
        "matematica - licenciatura diurno": "matemática",
        "matematica - bacharelado diurno": "matemática"
    })
    data = data.rename({attr: newattr}, axis=1)

    attrs.append(newattr)
    return data


def cic_courses(data):
    cic_courses = [
        'ciência da computação',
        'computação',
        'engenharia de computação',
        'engenharia mecatrônica'
    ]
    attr = 'course'
    data.drop(data.loc[~data[attr].isin(cic_courses)].index, inplace=True)
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


def ira(data, attrs):
    """Calculate the IRA (Academic Performance Index)."""
    attr = 'ira'
    attrs.append(attr)
    return data


def programming_subjects(data, attrs):
    """Isolate the initial programming subject."""

    attr = 'nome_disciplina'
    newattr = 'programming_subject'

    subjects = [
        'introdução à ciência da computação',
        'computacao basica',
        'algoritmos e programação de computadores',
        'algoritmos e estrutura de dados',
        'computacao para engenharia'
    ]

    data.drop(data[~data[attr].isin(subjects)].index, inplace=True)
    data.sort_values('periodo_cursou_disciplina')
    # keep the first occurrence (the earliest one)
    data.drop_duplicates(subset=['aluno'], inplace=True)

    notas = {
        'sr': -3,
        'ii': -2,
        'mi': -1,
        'cc': 1,
        'mm': 1,
        'ms': 2,
        'ss': 3
    }

    data[newattr] = 0

    for index, row in data.iterrows():
        if row['mencao_disciplina'] in notas:
            data.at[index, newattr] = notas[row['mencao_disciplina']]
        else:
            data.at[index, newattr] = 0
            # data.drop(index, inplace=True)

    attrs.append(newattr)
    return data


def subjects(data, attrs):
    """
    Generate an attribute for every subject, and for every semester,
    informing the student's grade (mention) numerically.
    It considers at most 20 of the most frequent
    subjects/semester from the first year.
    """

    def beyond_horizon(data):
        """
        Compare the student's entry with the semester the subject was attended,
        and remove it if it was attended beyond the horizon.
        """
        def horizon(row):
            year = 1  # 1 year = 2 semesters
            return (
                utils.date_to_real(row['periodo_cursou_disciplina']) -
                utils.date_to_real(row['periodo_ingresso_curso']) >= year
            )
        data.drop(data[data.apply(horizon, axis=1)].index, inplace=True)
        return data

    def subject_semester(data):
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

    data = beyond_horizon(data)
    data = subject_semester(data)

    attr_subject = 'nome_disciplina'
    attr_grade = 'mencao_disciplina'

    notas = {
        'sr': -3,
        'ii': -2,
        'mi': -1,
        'cc': 1,
        'mm': 1,
        'ms': 2,
        'ss': 3
    }
    # Transform the grades (mentions) into an number
    data[attr_grade] = data.apply(
        lambda x: notas[x[attr_grade]] if x[attr_grade] in notas else 0, axis=1
    )

    # Keep only the first occurrence of a subject/semester.
    data.sort_values('periodo_cursou_disciplina')
    data.drop_duplicates(subset=['aluno', attr_subject], inplace=True)

    # Keep only the 25 most frequent subjects/semester.
    n_subjects = 25
    subjects = data[attr_subject].value_counts()[0:n_subjects].index.to_list()
    data.drop(data.loc[~data[attr_subject].isin(subjects)].index, inplace=True)

    # Removes attributes that are different for a single student
    # (so we can use pivot_table)
    out = [
        'periodo_cursou_disciplina',
        'creditos_no_periodo',
        'creditos_aprovado_periodo',
        'creditos_disciplina',
    ]
    data = data.drop(columns=out)

    # Transform each subject into an attribute.
    index = data.columns.difference([attr_grade, attr_subject]).tolist()
    data = data.pivot_table(
        values=attr_grade,
        index=index,
        columns=attr_subject,
        aggfunc='first',
        fill_value=0,  # Not Attended
    ).reset_index()
    data.index.name = None

    subjects = data.columns.difference(index).tolist()
    attrs.extend(subjects)

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


def divide_course(data):
    """Return a dictionary with subsets of the data, separated by course."""
    attr = 'course'
    data_courses = {}
    for course in data[attr].unique():
        data_courses[course] = data.copy()[data[attr] == course]
        # data_courses[course].drop(attr, axis=1, inplace=True)

    return data_courses
