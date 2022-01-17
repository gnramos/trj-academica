# Pre Process Module

from hashlib import new
import utils


def gender(data, columns):
    """Tranform the gender attribute in a boolean and rename it."""
    attr = 'genero'
    newattr = 'female'
    data[newattr] = data.apply(lambda x: x[attr] == 'F', axis=1)

    columns.append(newattr)
    return data


def quota(data, columns):
    """Tranform the quota attribute in a boolean and rename it."""
    attr = 'sistema_cotas'
    newattr = 'quota'
    data[newattr] = data.apply(lambda x: x[attr] == 'Sim', axis=1)

    columns.append(newattr)
    return data


def public_school(data, columns):
    """Tranform the school type attribute in a boolean and rename it."""
    attr = 'Escola'
    newattr = 'public_school'
    data[newattr] = data.apply(lambda x: x[attr] == 'Publica', axis=1)

    columns.append(newattr)
    return data


def course(data, columns):
    """Group and rename the courses names."""
    attr = 'curso'
    newattr = 'course'

    data[newattr] = data.apply(lambda x: x[attr].lower(), axis=1)
    data[newattr] = data[newattr].replace({
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

    erase = ['Falecimento', 'Ativo']
    not_dropout = ['Formatura', 'CONCLUÍDO']

    data = data.drop(data.loc[data[attr].isin(erase)].index)
    data[newattr] = data.apply(lambda x: x[attr] not in not_dropout, axis=1)

    columns.append(newattr)
    return data


def ira(data, columns):
    """Calculate the IRA (Academic Performance Index)."""

    # TODO: calculate the ira according to student's mentions
    attr = 'IRA'
    newattr = 'ira'
    data[newattr] = data[attr]

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
