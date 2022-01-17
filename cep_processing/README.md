# Script para processamento do CEP

Este script ([**cep_gen.py**](cep_gen.py)) automatiza a extração informações do atributo CEP: o endereço, as coordenadas geográficas, e informações da rota entre o CEP e a Universidade de Brasília (UnB).

Os CEPs passam por um processo de formação prévia. Todas as informações adquiridas são armazenadas em arquivos JSON. É feita uma verificação previa nos arquivos antes de realizar uma requisição, para verificar se ela já foi realizada previamente, evitando trabalho inútil. Todos os processos podem ser interrompidos com uma exceção KeyboardInterrupt, ao iniciar novamente o script ele continuará de onde parou.


* A função responsável pela extração do endereço é a **request_address**, que utiliza o Web Service ViaCEP. As informações são armazenadas em um arquivo [**address.json**](files/address.json). Um delay é adicionado para que o serviço não bloqueie o acesso por quantidade de requisições em um período curto de tempo (o que torna o script lento, mas é a vida).

* A função responsável pela extração das coordenadas é a **request_coordinate**, que utiliza a API Geocoding do Google Maps Plataform. As informações são armazenadas em um arquivo [**coordinate.json**](files/coordinate.json). As coordenadas são requisitadas utilizando dos endereços obtidos na função request_address.


* A função responsável por adquirir informações sobre a rota entre os CEPs e a Universidade de Brasília é a **request_route**, que utiliza a API Distance Matrix do Google Maps Plataform. As informações são armazenadas em um arquivo [**route.json**](files/route.json). A rota é obtida atravez das cooordenadas obtidas na função request_coordinates, e da coordenada fixa da UnB.

Os serviços do Google Maps Plataform utilizam de uma chave do usuário, que deve ser inserida no arquivo de texto [**key**](key), presente no diretório.

Autor: Tiago de Souza Fernandes