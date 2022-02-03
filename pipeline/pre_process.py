# Pre Process Module

from hashlib import new
import utils


def format_data(data):
    """Remove leading and trailing spaces, and lowers all string elements."""
    def format(value):
        return value.str.strip().str.lower()

    data = data.apply(lambda x: format(x) if x.dtype == 'object' else x)
    data.columns = format(data.columns)
    return data


def gender(data, columns):
    """Tranform the gender attribute in a boolean and rename it."""
    attr = 'genero'
    newattr = 'female'
    data[newattr] = data.apply(lambda x: x[attr] == 'f', axis=1)

    columns.append(newattr)
    return data


def quota(data, columns):
    """Tranform the quota attribute in a boolean and rename it."""
    attr = 'sistema_cotas'
    newattr = 'quota'
    data[newattr] = data.apply(lambda x: x[attr] == 'sim', axis=1)

    columns.append(newattr)
    return data


def public_school(data, columns):
    """Tranform the school type attribute in a boolean and rename it."""
    attr = 'escola'
    newattr = 'public_school'
    data[newattr] = data.apply(lambda x: x[attr] == 'publica', axis=1)

    columns.append(newattr)
    return data


def credits(data, columns):
    """
    Rename the attribute of the amout of approved credits
    and remove non numerical values.
    """

    # TODO: generate this attribute for every semester
    # TODO: use the other credits attributes in the dataset
    attr = 'creditos_aprovado_periodo'
    newattr = 'approved_credits'
    data[newattr] = data.apply(
        lambda x: x[attr] if x.dtype == 'object' else 0, axis=1
    )

    columns.append(newattr)

    return data


def course(data, columns):
    """Group and rename the courses names."""
    attr = 'curso'
    newattr = 'course'

    data[newattr] = data[attr].replace({
        "controle e automação": "engenharia mecatrônica",
        "engenharia mecatrônica - " +
        "controle e automação": "engenharia mecatrônica",

        "informática": "computação",

        "matematica - licenciatura noturno": "matemática",
        "matematica - licenciatura diurno": "matemática",
        "matematica - bacharelado diurno": "matemática"
    })

    columns.append(newattr)
    return data


def dropout(data, columns):
    """Transform the way out attribute into a boolean dropout one."""
    attr = 'forma_saida_curso'
    newattr = 'dropout'

    erase = ['falecimento', 'ativo']
    not_dropout = ['formatura', 'concluído']

    data = data.drop(data.loc[data[attr].isin(erase)].index)
    data[newattr] = data.apply(lambda x: x[attr] not in not_dropout, axis=1)

    columns.append(newattr)
    return data


def ira(data, columns):
    """Calculate the IRA (Academic Performance Index)."""

    # TODO: calculate the ira according to student's mentions
    attr = 'ira'
    data[attr] = data[attr]

    columns.append(attr)
    return data


def programming_subjects(data, columns):
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
    data.drop_duplicates(subset=['aluno'], inplace=True)

    notas = {
        'SR': -3,
        'II': -2,
        'MI': -1,
        'CC': 1,
        'MM': 1,
        'MS': 2,
        'SS': 3
    }

    data[newattr] = 0

    for index, row in data.iterrows():
        if row['mencao_disciplina'] in notas:
            data.at[index, newattr] = notas[row['mencao_disciplina']]
        else:
            data.at[index, newattr] = 0
            # data.drop(index, inplace=True)

    columns.append(newattr)
    return data


def cep(data, columns):
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

    columns.append(newattr)
    return data


def divide_course(data):
    """Return a dictionary with subsets of the data, separated by course."""
    attr = 'course'
    data_courses = {}
    for course in data[attr].unique():
        data_courses[course] = data.copy()[data[attr] == course]

    return data_courses
