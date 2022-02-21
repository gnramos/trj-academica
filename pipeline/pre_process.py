# Pre Process Module

import unicodedata
import utils


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
    data[newattr] = data.apply(lambda x: x[attr] == 'f', axis=1)

    attrs.append(newattr)
    return data


def quota(data, attrs):
    """Tranform the quota attribute in a boolean and rename it."""
    attr = 'sistema_cotas'
    newattr = 'quota'
    data[newattr] = data.apply(lambda x: x[attr] == 'sim', axis=1)

    attrs.append(newattr)
    return data


def public_school(data, attrs):
    """Tranform the school type attribute in a boolean and rename it."""
    attr = 'escola'
    newattr = 'public_school'
    data[newattr] = data.apply(lambda x: x[attr] == 'publica', axis=1)

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

    data[newattr] = data.apply(
        lambda x: x[attr] if x[attr] in entry_types else 'outro', axis=1
    )

    attrs.append(newattr)
    return data


def credits(data, attrs):
    """
    Rename the attribute of the amout of approved credits
    and remove non numerical values.
    """

    # TODO: calculate this using the disciplines
    # TODO: generate this attribute for every semester
    # TODO: use the other credits attributes in the dataset
    attr = 'creditos_aprovado_periodo'
    newattr = 'approved_credits'
    data[newattr] = data.apply(
        lambda x: x[attr] if x.dtype == 'object' else 0, axis=1
    )

    attrs.append(newattr)

    return data


def course(data, attrs):
    """Group and rename the courses names."""
    attr = 'curso'
    newattr = 'course'

    data[newattr] = data[attr].replace({
        "engenharia mecatrônica - " +
        "controle e automação": "engenharia mecatrônica",
        "controle e automação": "engenharia mecatrônica",

        "informática": "computação",

        "matematica - licenciatura noturno": "matemática",
        "matematica - licenciatura diurno": "matemática",
        "matematica - bacharelado diurno": "matemática"
    })

    attrs.append(newattr)
    return data


def dropout(data, attrs):
    """Transform the way out attribute into a boolean dropout attribute."""
    attr = 'forma_saida_curso'
    newattr = 'dropout'

    erase = ['falecimento', 'ativo']
    not_dropout = ['formatura', 'concluído']

    data.drop(data.loc[data[attr].isin(erase)].index, inplace=True)
    data[newattr] = data.apply(lambda x: x[attr] not in not_dropout, axis=1)

    attrs.append(newattr)
    return data


def ira(data, attrs):
    """Calculate the IRA (Academic Performance Index)."""

    # TODO: calculate the ira according to student's mentions
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
    Generate an attribute for every subject, informing the student's
    grade (mention) numerically.
    It considers at most 20 of the most frequent subjects from the first year.
    """

    def beyond_horizon(row):
        """
        Compare the student's entry with the semester the subject was attended,
        and check if it was attended within the horizon.
        """
        horizon_years = 1  # 1 year = 2 semesters
        return (
            utils.date_to_real(row['periodo_cursou_disciplina']) -
            utils.date_to_real(row['periodo_ingresso_curso']) >= horizon_years
        )

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

    # Remove subjects done after the horizon.
    data.drop(data[data.apply(beyond_horizon, axis=1)].index, inplace=True)

    # Keep only the first occurrence of a subject.
    # TODO: consider the other attempts.
    data.sort_values('periodo_cursou_disciplina')
    data.drop_duplicates(subset=['aluno', attr_subject], inplace=True)

    print(data.shape)
    # Keep only the 20 most frequent subjects.
    n_subjects = 20
    subjects = data[attr_subject].value_counts()[0:n_subjects].index.to_list()
    data.drop(data.loc[~data[attr_subject].isin(subjects)].index, inplace=True)

    print(data.shape)
    # Transform each subject into an attribute.
    index = data.columns.difference([attr_grade, attr_subject]).tolist()
    data = data.pivot_table(
        values=attr_grade,
        index=index,
        columns=attr_subject,
        aggfunc='first',
        fill_value=0,  # Not Attended
    ).reset_index()

    print(data.shape)

    subjects = data.columns.difference(index).tolist()

    attrs.extend(subjects)

    return data


def cep(data, attrs):
    """
    Transform the cep into the distance from the student's home
    to the University of Brasília. Uses the data requested using the
    cep_gen.py script.
    """

    attr = 'cep'
    newattr = 'distance'

    route_json = utils.read_json('../data/route.json')
    address_json = utils.read_json('../data/address.json')
    # coordinate_json = utils.read_json('../data/coordinate.json')
    data[attr] = data.apply(lambda x: utils.format_cep(x[attr]), axis=1)

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
