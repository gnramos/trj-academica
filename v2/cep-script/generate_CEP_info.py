import json
import requests
import pandas as pd
import time

# Create a list of unique cep values from the database.
def unique_ceps():
    file = 'meca.csv'
    df = pd.read_csv(file, low_memory=False)
    cep_list = df['CEP'].drop_duplicates().tolist()
    cep_list = [str(cep).zfill(8) for cep in cep_list]  # add leading zeros
    return cep_list


# Manipulate data of a integer stored in a file
def write_num(id):
    with open('id.txt', 'w') as f:
        f.write('%d' % id)

def read_num():
    with open('id.txt', 'r') as f:
        return f.read()


# Manipulate data from .json files.
def write_json(via_cep_info, file_name):
    with open(file_name+'.json', 'w') as outfile:
        json.dump(via_cep_info, outfile, indent=4, sort_keys=True)

def read_json(file_name):
    with open(file_name+'.json', 'r') as outfile:
        return json.load(outfile)


#####################################################################


# Request cep data for all the unique ceps.
def request_cep_info(cep_list):

    # Request cep data from the viaCEP api.
    def request_via_cep(cep):
        url = f'https://viacep.com.br/ws/{cep}/json/'
        return json.loads(requests.get(url).text)

    # Limit of requests, counting from the last one made.
    sz = len(cep_list)
    # sz = 1100

    via_cep_info = read_json('via_cep_info')
    id = int(read_num())  # last index not requested yet
    for i in range(id, sz):
        cep = cep_list[i]
        print(f'{cep} => {i}/1286')
        try:
            time.sleep(5) # so viacep don't block us
            info = request_via_cep(cep)
        except Exception as e: 
            print(e)
            write_num(i)  # save the id
            write_json(via_cep_info, 'via_cep_info')  # save the data
            return

        via_cep_info[cep] = info  # add info to the data

    write_json(via_cep_info, 'via_cep_info')
    print('deu bom')




# Request route (cep-unb) info for all the unique ceps.
def request_route_info(cep_list):

    # Request route info using Google Maps Matrix Distance.
    def request_google_maps(address1, address2):
        key = '' # insert key
        request = requests.get(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric'
                               f'&origins={address1}&destinations={address2}&key={key}')
        return json.loads(request.text)

    # Use the cep info to return the adress of that cep.
    def get_adress(cep, via_cep_info):
        info = via_cep_info[cep]
        # adress = info['logradouro'] + ' ' + info['bairro'] + ' ' + info['localidade'] + ' ' + info['uf']
        adress = info['bairro'] + ' ' + info['uf']
        return adress


    google_maps_info = read_json('google_maps_info')
    via_cep_info = read_json('via_cep_info')
    cep_unb = '70910900'
    adress_unb = get_adress(cep_unb, via_cep_info)

    sz = len(google_maps_info)

    for cep in cep_list:
        if cep not in google_maps_info:

            try:
                adress_origin = get_adress(cep, via_cep_info)
            except Exception:
                print(f'{cep} => sem dados de cep.')
                continue


            print(f'processando {cep}... {sz}/1286')
            sz+=1
            try:
                info = request_google_maps(adress_origin, adress_unb)
            except Exception as e: 
                print(e)
                print(f'erro no cep {cep}.')
                write_json(google_maps_info, 'google_maps_info')  # save the data
                return

            google_maps_info[cep] = info  # add info to the data


    write_json(google_maps_info, 'google_maps_info')

def fillCEP():
    pass


# 1286 unique ceps
cep_list = unique_ceps()


# write_num(0)
# request_cep_info(cep_list)
# 70 erro

# cep_list = ['71015214', '73045173', '00000000']
request_route_info(cep_list)
# 18 ZERO_RESULTS
# 3 NOT_FOUND

# cep_info_generator()
# cep_info_show()