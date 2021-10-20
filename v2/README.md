# Preditor de Evasão

Este preditor foi implementado de forma modularizada, cada módulo possui funções com objetivos específicos, utilizados pelo pipeline para ler a entrada, pre-processar e processar os dados, treinar os algoritmos e gerar os resultados do trabalho.

A partir de modificações pontuais em certos parâmetros e variáveis dos arquivos, é possível gerar diferentes modelos de dados para o treinamento dos algoritmos.


- [*main.py*](main.py): Arquivo principal, recebe os dados de entrada e gera os resultados seguindo o pipeline definido no projeto.

- [*pre_process.py*](pre_process.py): Contém funções responsáveis pelo pré-processamento da base de dados.

- [*process.py*](process.py): Contém funções responsáveis processamento da base, treinando os algoritmos e gerando predições a cerca dos conjuntos de testes.

- [*parameters.py*](parameters.py): Contém os hiperparâmetros utilizados pelos algoritmtos.

- [*materias.json*](materias.json): Possui uma relação entre os códigos das disciplinas obrigatórias do curso e informações como quantidade de créditos e nome da disciplina.

- [*analysis.py*](analysis.py): Contém funções para a visualização gráfica dos dados.

- [*helpers.py*](helpers.py): Contém algumas funções auxiliares.

- [*generate_CEP_info.py*](cep-script/generate_CEP_info.py): Possui alguns scripts para gerarem a distância de um CEP qualquer para a UnB, utilizando do webservice viacep.com.br e da Distance Matrix API do Google Maps.

Autor: Tiago de Souza Fernandes

## Referências

* [Apresentação do trabalho](https://www.youtube.com/watch?v=A0dwd8XpOvo)