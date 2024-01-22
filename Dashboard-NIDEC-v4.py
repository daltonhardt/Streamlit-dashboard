############################
#   NIDEC RFID DASHBOARD   #
#   Author: Dalton Hardt   #
#   Date:  Jan/24          #
############################

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import time

################################################################################################
# Para mostrar todas as linhas e colunas do Dataframe
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('max_colwidth', 25)

################################################################################################
# Constantes iniciais
inicio, fim = ['05:00:00', '22:00:00']
hora_inicio_semana = '05:00:00'
hora_troca_semana = '13:30:00'
hora_saida_semana = '22:00:00'
hora_inicio_sabado = '05:00:00'
hora_troca_sabado = '09:00:00'
hora_saida_sabado = '13:00:00'
horas_dia_semana = 8
horas_dia_sabado = 4

################################################################################################
# Definindo lista com cores para os Operadores
cores = ['coral', 'limegreen', 'dodgerblue', 'yellow', 'deepskyblue', 'pink', 'lightsalmon', 'orange',
         'cyan', 'magenta', 'lime', 'gold', 'silver', 'beige', 'khaki', 'turquoise',
         'lavender', 'whitesmoke', 'palegreen', 'lightsteelblue', 'aquamarine', 'tomato', 'lightgray', 'tan',
         'gray', 'cadetblue', 'yellowgreen', 'violet', 'darkkhaki', 'hotpink', 'darkcyan', 'orangered',
         'coral', 'limegreen', 'dodgerblue', 'yellow', 'deepskyblue', 'pink', 'lightsalmon', 'orange',
         'cyan', 'magenta', 'lime', 'gold', 'silver', 'beige', 'khaki', 'turquoise',
         'lavender', 'whitesmoke', 'palegreen', 'lightsteelblue', 'aquamarine', 'tomato', 'lightgray', 'tan',
         'gray', 'cadetblue', 'yellowgreen', 'violet', 'darkkhaki', 'hotpink', 'darkcyan', 'orangered']
df_cores = pd.DataFrame(cores, columns=['Cor'])  # Definindo o dataframe com a lista de cores


################################################################################################
# Função para buscar as Horas de início e termino dos turnos
def busca_horas_turno(dia_semana, hora_dia, minuto):
    if dia_semana in ('Sab', 'Sat') and hora_dia in ('04', '05', '06', '07', '08'):
        hora_entrada = '05:00'
        hora_saida = [9, 0]  # às 09:00 (Hora e Minutos como inteiros)
    elif dia_semana in ('Sab', 'Sat') and hora_dia in ('09', '10', '11', '12'):
        hora_entrada = '09:00'
        hora_saida = [13, 0]  # às 13:00 (Hora e Minutos como inteiros)
    elif dia_semana in ('Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri') and \
            hora_dia in ('04', '05', '06', '07', '08', '09', '10', '11', '12'):
        hora_entrada = '05:00'
        hora_saida = [13, 30]  # às 13:30 (Hora e Minutos como inteiros)
    elif dia_semana in ('Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri') and \
            hora_dia == '13' and minuto <= 30:
        hora_entrada = '05:00'
        hora_saida = [13, 30]  # às 13:30 (Hora e Minutos como inteiros)
    else:
        hora_entrada = '13:30'
        hora_saida = [22, 0]  # às 22:00 (Hora e Minutos como inteiros)

    return hora_entrada, hora_saida


################################################################################################
# Função para ajustar o Dataframe incluindo registros de ENTRADA e SAIDA quando não registrados pelo Operador
def ajusta_dataframe():
    # Criando um dataframe com cabeçalho
    global row, registro
    cabecalho = ['Data', 'Evento', 'Nome', 'Matricula', 'Posto', 'AnoMes', 'Dia', 'Hora', 'Minuto', 'Cor']
    df_new = pd.DataFrame(columns=cabecalho)
    df_agrupado_por_dia = df_filtrado.groupby('Dia')  # criando um dataframe agrupado por DIA e
    # print('\n\n========== AJUSTANDO O DATAFRAME ==========')
    for chave, reg in df_agrupado_por_dia:
        # print('[][][][][] Dia (key):', chave)
        novo_dia = True
        registro_anterior = []
        for index, row in reg.iterrows():
            registro = row.tolist()
            # print('[]')
            # print('registro anterior   :', registro_anterior)
            # print('registro atual (row):', registro)

            if novo_dia:  # o dia é novo ou mudou e precisa começar com uma ENTRADA
                # print('novo_dia=', novo_dia)
                if row['Evento'] == 'ENTRADA':
                    # print('   Primeiro EVENTO desse dia começa como ENTRADA. Gravando a linha no df_new')
                    df_new.loc[len(df_new)] = registro
                    registro_anterior = registro
                    novo_dia = False
                else:
                    # print('   Primeiro EVENTO desse dia começa como SAIDA. Gravando a linha no df_new como ENTRADA')
                    registro[1] = 'ENTRADA'  # para criar um evento de SAIDA
                    df_new.loc[len(df_new)] = registro
                    registro_anterior = registro
                    novo_dia = False

            else:  # ainda processando os Eventos no mesmo dia

                if row['Evento'] == 'ENTRADA' and registro_anterior[1] == 'SAIDA':
                    # print('   > E/S do mesmo Operador - tudo certo! gravar registro')
                    df_new.loc[len(df_new)] = registro
                    registro_anterior = registro

                elif row['Evento'] == 'ENTRADA' and registro_anterior[1] == 'ENTRADA':
                    if row['Nome'] == registro_anterior[2]:  # se for o mesmo Operador
                        # print('   > E/E do mesmo Operador sem ter dado SAIDA antes - criando a SAIDA')
                        novo_registro = registro_anterior
                        novo_registro[0] = registro[0]  # Hora da saida igual da Entrada do corrente Operador
                        novo_registro[1] = 'SAIDA'  # para criar um evento de SAIDA
                        novo_registro[7] = registro[7]  # Hora da saida igual da Entrada do corrente Operador
                        novo_registro[8] = registro[8]  # Minuto da saida igualda Entrada do corrente Operador
                        df_new.loc[len(df_new)] = novo_registro  # cria registro SAIDA para o Operador de antes
                        df_new.loc[len(df_new)] = registro  # grava o registro de ENTRADA do Operador atual
                        registro_anterior = registro
                    else:  # se não for o mesmo Operador
                        # print('   > E/E de outro Operador sem que o de antes tenha dado SAIDA - criando a SAIDA')
                        novo_registro = registro_anterior
                        novo_registro[0] = registro[0]  # Hora da saida igual da Entrada do corrente Operador
                        novo_registro[1] = 'SAIDA'  # para criar um evento de SAIDA
                        # novo_registro[2] = registro_anterior[2]  # Nome do Operador
                        # novo_registro[3] = str(registro_anterior[3])  # Matricula do Operador
                        novo_registro[7] = registro[7]  # Hora da saida igual da Entrada do corrente Operador
                        novo_registro[8] = registro[8]  # Minuto da saida igual da Entrada do corrente Operador
                        # novo_registro[9] = registro_anterior[9]  # Cor associada
                        df_new.loc[len(df_new)] = novo_registro  # grava novo registro com dados do Operador de antes
                        df_new.loc[len(df_new)] = registro  # grava o registro de ENTRADA do Operador atual
                        registro_anterior = registro

                elif row['Evento'] == 'SAIDA' and registro_anterior[1] == 'ENTRADA':
                    if row['Nome'] == registro_anterior[2]:  # se for o mesmo Operador
                        # print('   > S/E do mesmo Operador - tudo certo! grava o registro corrente de SAIDA')
                        df_new.loc[len(df_new)] = registro
                        registro_anterior = registro
                    else:  # se não for o mesmo Operador
                        # print('   > S/E por um Operador diferente, grava essa SAIDA para o Operador anterior')
                        novo_registro = row.tolist()
                        novo_registro[2] = registro_anterior[2]  # Nome do Operador
                        novo_registro[3] = str(registro_anterior[3])  # Matricula do Operador
                        novo_registro[9] = registro_anterior[9]  # Cor associada
                        df_new.loc[len(df_new)] = novo_registro  # grava novo registro com dados do Operador de antes
                        # grava o registro atual como ENTRADA
                        novo_registro = row.tolist()
                        # print('2**** registro_temp:', registro_temp)
                        novo_registro[1] = 'ENTRADA'
                        # print('3**** registro_temp:', registro_temp)
                        df_new.loc[len(df_new)] = novo_registro  # grava o registro do Operador atual como ENTRADA
                        # print('4**** registro_temp:', registro_temp)
                        registro_anterior = novo_registro
                        # print('5**** registro_anterior:', registro_anterior)

                elif row['Evento'] == 'SAIDA' and registro_anterior[1] == 'SAIDA':
                    if row['Nome'] == registro_anterior[2]:  # se for o mesmo Operador
                        # print('   > S/S pelo mesmo Operador -> Adicionando ENTRADA e SAIDA para o Operador')
                        novo_registro = registro_anterior
                        novo_registro[1] = 'ENTRADA'  # para criar um evento de ENTRADA
                        df_new.loc[len(df_new)] = novo_registro  # grava novo registro de ENTRADA com dados do Operador de antes
                        df_new.loc[len(df_new)] = registro  # grava o registro atual de SAIDA do Operador corrente
                        registro_anterior = registro
                    else:  # se não for o mesmo Operador
                        # print('   > S/S por Operador diferente -> Adicionando ENTRADA e SAIDA para Operador corrente')
                        novo_registro = row.tolist()
                        novo_registro[0] = registro_anterior[0]  # Data da saida igual da Entrada do corrente Operador
                        novo_registro[1] = 'ENTRADA'  # para criar um evento de ENTRADA
                        novo_registro[2] = registro[2]  # Nome do Operador
                        novo_registro[3] = str(registro[3])  # Matricula do Operador
                        novo_registro[7] = registro_anterior[7]  # Hora da saida igual da Entrada do corrente Operador
                        novo_registro[8] = registro_anterior[8]  # Minuto da saida igual da Entrada do corrente Operador
                        novo_registro[9] = registro[9]  # Cor associada
                        df_new.loc[len(df_new)] = novo_registro  # grava novo registro com dados do Operador de antes
                        df_new.loc[len(df_new)] = registro  # grava o registro do Operador atual
                        registro_anterior = registro

        # se ultimo registro foi ENTRADA então cria uma SAIDA no final do turno
        # print('Evento = Entrada?', row['Evento'], 'registro_anterior[1] = Entrada?', registro_anterior[1])
        if row['Evento'] == 'ENTRADA' or registro_anterior[1] == 'ENTRADA':
            dia_na_semana = registro[0].strftime('%a')
            # print('.....dia_semana', dia_na_semana)
            hora_no_dia = registro[0].strftime('%H')
            # print('.....hora_dia', hora_no_dia)
            minuto_na_hora = int(registro[0].strftime('%M'))
            # print('.....minuto', minuto_na_hora)

            entrada_turno, saida_turno = busca_horas_turno(dia_na_semana, hora_no_dia, minuto_na_hora)

            novo_registro = row.tolist()
            novo_registro[0] = registro[0].replace(hour=saida_turno[0], minute=saida_turno[1])
            novo_registro[1] = 'SAIDA'
            novo_registro[7] = saida_turno[0]
            novo_registro[8] = saida_turno[1]
            # print('*** gravando ULTIMO registro DO DIA como SAIDA: ', novo_registro)
            df_new.loc[len(df_new)] = novo_registro

    # Retirando as linhas duplicadas
    df_new = df_new.drop_duplicates(subset=['Data', 'Evento', 'Nome'], keep=False).reset_index(drop=True)
    return df_new


################################################################################################
# Iniciando o streamlit
st.set_page_config(page_title="RFID Dashboard v4", page_icon="✅", layout="wide")
st.image('./logoNidec.png')
st.title("RFID Dashboard - Itaiópolis")

# Lendo o arquivo CSV
uploaded_file = st.sidebar.file_uploader('Escolha o arquivo (.csv)', type='csv')

if uploaded_file is not None:
    with st.spinner('Processando...'):
        time.sleep(1)

    if uploaded_file.type == "text/csv":
        # print('lendo o arquivo e transformando em um Dataframe Pandas')
        try:
            df_original = pd.read_csv(uploaded_file, dtype={'Matricula': object})  # lendo a coluna Matricula como string
            list_of_header = list(df_original.columns)
            if list_of_header == ['Data', 'Evento', 'Nome', 'Matricula', 'Posto']:
                # Arquivo é do tipo CSV e tem os HEADERS definidos
                arq_tipo = 'csv_com_header'
                # print('tipo=', arq_tipo)
            else:
                # Arquivo é do tipo CSV MAS não tem os HEADERS definidos
                arq_tipo = 'csv_sem_header'
                # print('tipo=', arq_tipo)
        except UnicodeDecodeError:
            arq_tipo = 'UnicodeDecodeError'

    else:
        # arquivo não é do tipo CSV
        arq_tipo = 'no_csv'

    if arq_tipo == 'csv_com_header':
        # retirando espaços em branco ante e depois nas colunsa tipo 'object' (=texto)
        df_original = df_original.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        # print('\n\ndf_original:\n', df_original)

        # filtrando para ficar somente com os eventos de ENTRADA e de SAIDA
        df = df_original[(df_original['Evento'] == 'ENTRADA') | (df_original['Evento'] == 'SAIDA')].reset_index(
            drop=True)

        if not df.empty:
            # ajustando algumas colunas
            for i, linha in df.iterrows():
                try:
                    linha['Data'] = datetime.strptime(linha['Data'], "%d/%m/%Y %H:%M")  # formato de Data válida
                    # print(i, " OK Data válida")
                except ValueError:
                    # print(i, " xxxx Data inválida!!! - removendo a linha")
                    df.drop(df.index, inplace=True)

            # Substituindo Nome e Matricula se estiver em branco ou Null
            df.Nome = df.Nome.fillna('Sem Nome')  # substituindo pela ‘string’ 'Sem Nome'
            df.Matricula = df.Matricula.fillna('Sem Matricula')  # substituindo pela ‘string’ 'Sem Matricula'
            # print('\n\ndf sem as Datas Invalidas:\n', df)
            df['Data'] = pd.to_datetime(df["Data"], dayfirst=True)
            df['AnoMes'] = df["Data"].apply(lambda x: str(x.month) + "-" + str(x.year))  # criando coluna Mes-Ano
            df['Matricula'] = df['Matricula'].astype(str)  # deixando a coluna Matricula como String
            df['Dia'] = df['Data'].dt.strftime('%d').astype(int)  # criando a coluna somente com o dia do mês
            df['Hora'] = df['Data'].dt.strftime('%H').astype(int)  # criando a coluna somente com Hora e Minuto do dia
            df['Minuto'] = df['Data'].dt.strftime('%M').astype(int)  # criando a coluna somente com Hora e Minuto do dia

            # associando as cores unicas para cada Operador
            operadores = df['Nome'].unique()  # criando lista com os nomes dos Operadores
            df_operadores = pd.DataFrame(operadores, columns=['NomeOperador'])  # criando um dataframe
            df_operador_cor = pd.merge(df_operadores, df_cores, left_index=True,
                                       right_index=True)  # mesclando os dataframes
            # print('df_operador_cor: \n', df_operador_cor)

            # adicionando as cores ao dataframe original
            df = pd.merge(df, df_operador_cor, left_on='Nome', right_on='NomeOperador',
                          how='inner').sort_values(by='Data', ascending=True).reset_index(drop=True)
            # print('df após o merge com as cores: \n', df)
            # ajustando algumas colunas
            df = df.drop(columns=['NomeOperador'])  # Deletando a coluna NomeOperador
            # df = df.drop_duplicates()  # Retirando as linhas duplicadas
            df = df.drop_duplicates(subset=['Data', 'Evento', 'Nome'], keep=False)  # Retirando as linhas duplicadas
            df = df.apply(
                lambda x: x.str.strip() if x.dtype == 'object' else x)  # removendo espaço das colunas string (object)

            # Criando um SelectBox para selecionar o Ano e o Mes como chave de busca
            st.sidebar.header('Escolha os filtros:')
            var_ano_mes = st.sidebar.selectbox("Selecione o Mês e Ano", df['AnoMes'].drop_duplicates())
            # Criando um SelectBox para selecionar o Posto de Trabalho como chave de busca
            var_posto = st.sidebar.selectbox("Selecione o Posto de Trabalho",
                                             df["Posto"].drop_duplicates().sort_values())
            # Criando um CheckBox para marcar se quer Todos os Operadores ou não
            var_todos_operadores = st.sidebar.checkbox("Todos Operadores", value=True)

            # filtra o Dataframe com o Ano-Mes e Posto escolhidos, inicialmente com Todos os nomes de Operadores
            df_filtrado = df[(df['AnoMes'] == var_ano_mes) & (df['Posto'] == var_posto) &
                             (df['Evento'].isin(['ENTRADA', 'SAIDA']))].sort_values(by='Data',
                                                                                    ascending=True).reset_index(
                drop=True)
            # print('\n\n ANTES de ajustar o dataframe:\n', df_filtrado)

            # filtrando para tirar os registros com Datas iguais independente do Evento
            # df_filtrado = df_filtrado.drop_duplicates(['Data', 'Nome'], keep=False)
            df_filtrado = df_filtrado.drop_duplicates(['Data'])
            # print('\n\ndf sem as duplicadas de Data e Nome:\n', df_filtrado)

            ######################################################################################
            # chamando a função para ajeitar as linhas do dataframe
            df_final = ajusta_dataframe()
            # print('\n\nDEPOIS de ajustar o dataframe:\n', df_final)
            ######################################################################################

            # criando um dataframe somente com os eventos de ENTRADA (=2)
            df_entradas = df_final[(df_final['Evento'] == 'ENTRADA')].reset_index(drop=True)
            # print('df_entradas:\n', df_entradas)

            # criando um dataframe somente com os eventos de SAIDA (=3)
            df_saidas = df_final[(df_final['Evento'] == 'SAIDA')].reset_index(drop=True)
            # print('df_saidas:\n', df_saidas)

            # Pegando o Primeiro e o último dia do mês selecionado
            first_day_month = 1
            # print('first_day_month: ', first_day_month)
            last_day_month = pd.Timestamp(df_entradas['Data'].max()).days_in_month
            # print('last_day_month: ', last_day_month)
            datas_eventos = df_entradas['Data'].unique().tolist()
            # print('datas_eventos: ', datas_eventos)

            dia_atual = []
            dias = []
            for i, dia in enumerate(datas_eventos):
                dia = [dia.strftime('%a'), dia.strftime('%d')]
                if dia != dia_atual:
                    dias.append(dia)
                    dia_atual = dia
            # print('dias:', dias)
            horas_disponiveis = 0
            horas_dia_semana = 8
            horas_dia_sabado = 4
            for i, dia in enumerate(dias):
                if dia[0] in ('Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri'):
                    horas_disponiveis += horas_dia_semana
                else:
                    horas_disponiveis += horas_dia_sabado
            # print('TOTAL horas disponiveis no periodo =', horas_disponiveis)

            if var_todos_operadores:  # se o checkBox estiver marcado com TODOS Operadores
                # operadores = df_entradas['Nome'].unique()  # pega os nomes unicos do dataframe
                df_operadores = df_entradas.drop_duplicates(subset=['Nome', 'Cor'])
                lista_operadores = df_operadores[['Nome', 'Cor']].values.tolist()
                lista_operadores.sort()  # coloca a lista em ordem alfabética
            else:
                seleciona_operador = df_entradas['Nome'].unique()  # cria lista com nomes dos operadores
                seleciona_operador.sort()  # coloca a lista em ordem alfabética
                var_operador = st.sidebar.selectbox("Selecione o Operador",
                                                    seleciona_operador)  # cria o selectbox para escolher o Operador
                # filtra o Dataframe com o Ano-Mes e Posto escolhidos e com o nome do Operador selecionado
                df_entradas = df_entradas[(df_entradas['AnoMes'] == var_ano_mes) & (df_entradas['Posto'] == var_posto) &
                                          (df_entradas['Nome'] == var_operador)].sort_values(by='Data',
                                                                                             ascending=True).reset_index(
                    drop=True)
                df_saidas = df_saidas[(df_saidas['AnoMes'] == var_ano_mes) & (df_saidas['Posto'] == var_posto) &
                                      (df_saidas['Nome'] == var_operador)].sort_values(by='Data',
                                                                                       ascending=True).reset_index(
                    drop=True)
                df_operadores = df_entradas.loc[df_entradas['Nome'].str.strip() == var_operador].reset_index(drop=True)
                # print('df_operadores: \n', df_operadores)
                df_operadores = df_operadores.drop_duplicates(subset=['Nome', 'Cor'], keep='first').reset_index(
                    drop=True)
                # print('df_operadores..: \n', df_operadores)
                lista_operadores = df_operadores[['Nome', 'Cor']].values.tolist()
                lista_operadores.sort()  # coloca a lista em ordem alfabética

            # criando um dicionário a partir da lista de operadores para armazenar as horas de trabalho de cada operador
            lista = []
            for i in range(len(lista_operadores)):
                item = str(lista_operadores[i][0])
                item = item.replace(" ", "")
                lista.append(item)
            contador_horas = dict.fromkeys(lista, [0.0, 0.0])

            # transformando a coluna 'Data' em tipo datetime64 no formato 'Y-m-d H:M:S'
            df_entradas['Data'] = pd.to_datetime(df_entradas["Data"], dayfirst=False)
            df_entradas['Data'] = df_entradas['Data'].dt.strftime('%d-%m-%Y %H:%M')

            df_saidas['Data'] = pd.to_datetime(df_saidas["Data"], dayfirst=False)
            df_saidas['Data'] = df_saidas['Data'].dt.strftime('%d-%m-%Y %H:%M')

            # processando as linhas do grafico
            if not df_entradas.empty:
                # definindo as listas com datas de entrada e saida e formatando para '%d-%m-%Y %H:%M'
                datas_entradas = df_entradas['Data'].tolist()
                inicio_dia = datas_entradas[0]
                inicio_dia = datetime.strptime(inicio_dia, '%d-%m-%Y %H:%M')
                inicio_dia = inicio_dia.replace(day=1, hour=5, minute=0)
                fim_dia = inicio_dia.replace(day=1, hour=22, minute=0)

                datas_entradas = [datetime.strptime(data, '%d-%m-%Y %H:%M') for data in datas_entradas]

                datas_saidas = df_saidas['Data'].tolist()
                datas_saidas = [datetime.strptime(data, '%d-%m-%Y %H:%M') for data in datas_saidas]

                # Criando uma lista de datas com espaçamentos de uma hora entre 05:00 e 22:00
                entrada = datetime.strptime(df_entradas['Data'][0], '%d-%m-%Y %H:%M')
                mes = entrada.strftime('%m')
                ano = entrada.strftime('%Y')
                data_inicial = datetime(int(ano), int(mes), 1, 5, 0,
                                        0)  # Data inicial: ano, mês, dia, hora, minuto, segundo
                espacamento = timedelta(hours=1)  # Espaçamento de 1 hora
                num_horas = 18  # Número de horas entre as 5:00 e as 22:00
                lista_de_horas = [data_inicial + i * espacamento for i in range(num_horas)]  # gerando a lista

                fig, ax = plt.subplots(figsize=(8, 5))
                # print('lista_operadores:', lista_operadores)

                # criando as linhas do gráfico
                duracao = 0
                for (index1, row1), (index2, row2) in zip(df_entradas.iterrows(), df_saidas.iterrows()):
                    entrada = datetime.strptime(row1['Data'], '%d-%m-%Y %H:%M')
                    dia = entrada.strftime('%d')
                    entrada = entrada.replace(day=1)

                    saida = datetime.strptime(row2['Data'], '%d-%m-%Y %H:%M')
                    saida = saida.replace(day=1)

                    pessoa = row1['Nome']
                    # print('duracao=', duracao)

                    # a duracao de tempo em que o Operador ficou no posto
                    duracao = round(((saida - entrada).total_seconds() / 3600), 2)  # convertendo para horas
                    # print(pessoa, 'no dia', dia, 'entrou às', row1['Hora'], ':', row1['Minuto'], 'e saiu às',
                    #      row2['Hora'], ':', row2['Minuto'], ' [', duracao, ']')

                    nome = row1['Nome'].replace(" ", "")
                    # carregando o dicionário com a duração do Operador no Posto e o percentual sobre o tempo disponivel
                    for key in contador_horas.keys():
                        # print('key:', key, 'nome:', nome)
                        if key == nome:
                            contador_horas[key] = contador_horas[key].copy()  # >>> Para não propagar para outras chaves
                            contador_horas[key][0] = contador_horas[key][0] + duracao
                            contador_horas[key][1] = contador_horas[key][0] / horas_disponiveis
                            # print(contador_horas[key], '', contador_horas[key][0])

                    # criando as linhas horizontais
                    ax.hlines(dia, entrada, saida, color=row1['Cor'], linewidth=20, label=row1['Nome'])
                    # Adicionando texto com a duração se duracao pelo menos de 9 minutos (aprox. 0.15)
                    if 0.25 <= duracao < 0.5:
                        ax.text(saida, dia, f'{duracao:.2f}h', verticalalignment='bottom', horizontalalignment='right',
                                fontsize=4)
                    elif 0.5 <= duracao < 1:
                        ax.text(saida, dia, f'{duracao:.2f}h', verticalalignment='top', horizontalalignment='right',
                                fontsize=5)
                    elif duracao >= 1:
                        ax.text(saida, dia, f'{duracao:.2f}h', verticalalignment='center', horizontalalignment='right',
                                fontsize=7, mouseover='True')
                # Criando uma legenda separada com os nomes dos Operadores na cor específica
                plt.legend()
                linhas_legenda = []
                for item in lista_operadores:
                    linha, = ax.plot([], [], label=item[0], color=item[1], linewidth=12)
                    linhas_legenda.append(linha)
                ax.legend(title='Legenda:', handles=linhas_legenda, loc='upper left', bbox_to_anchor=(1, 1))

                # Adicionando rótulos e título
                ax.set_xlabel('      Hora      ', size=12, bbox=dict(alpha=0.05), labelpad=12)
                ax.set_ylabel('      Dia      ', size=12, bbox=dict(alpha=0.05), labelpad=12)
                plt.xticks(rotation=90)

                # definindo os limites e a formatação do grid no eixo X
                lims = (inicio_dia, fim_dia)
                locator = mdates.AutoDateLocator(minticks=5, maxticks=20)
                formatter = mdates.ConciseDateFormatter(locator)
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
                ax.set_xlim(lims)

                ax.grid(True)  # ativando o grid
                ax.grid(axis='x', which="major", linewidth=0.7)  # customizando grid Maior somente no eixo X
                ax.grid(axis='x', which="minor", linewidth=0.5,
                        alpha=0.25)  # customizando o grid Menor somente no eixo X
                ax.minorticks_on()  # ativando os ticks menores
                ax.yaxis.set_tick_params(which='minor', bottom=False)  # desativando os ticks menores no eixo Y
                ax.tick_params(axis='x', direction='out', length=13, width=2)  # customizando os ticks no eixo X

                plt.title(f'Operadores no Posto de Trabalho {var_posto} em {var_ano_mes}', pad=5, fontsize=12,
                          fontweight='bold')

                st.pyplot(fig)

                # print('DICIONARIO contador_horas:', contador_horas)
                contador_horas_v1 = {k: round(v[0], 2) for k, v in contador_horas.items()}
                contador_horas_v1 = dict(sorted(contador_horas_v1.items()))
                # print('dicionario contador de horas PRIMEIRO VALOR:\n', contador_horas_v1)

                contador_horas_v2 = {k: round(v[1], 4) for k, v in contador_horas.items()}
                contador_horas_v2 = dict(sorted(contador_horas_v2.items()))
                # print('dicionario contador de horas SEGUNDO VALOR:\n', contador_horas_v2)

                # criando e mostrando as METRICAS de horas trabalhadas de cada Operador
                st.divider()
                st.markdown(f'#### Total de Horas por Operador em {var_ano_mes}')
                st.markdown(
                    f'##### Percentual trabalhado com base nas {horas_disponiveis} horas disponiveis em cada Turno')
                st.markdown(
                    '''
                            <style>
                            [data-testid="stMetricValue"] {
                                font-size: 200%;
                            }
                            </style>
                            <style>
                            [data-testid="stMetricDelta"] svg {
                                transform: rotate(90deg);
                                display: none;
                            }
                            </style>
                            ''', unsafe_allow_html=True)

                lista_chaves = list(contador_horas_v1.keys())
                lista_valor_1 = list(contador_horas_v1.values())
                lista_valor_2 = list(contador_horas_v2.values())
                col_list = st.columns(
                    len(lista_chaves))  # criando o número de colunas de acordo com o numero de Operadores
                for i, vcol in enumerate(col_list):
                    if lista_valor_2[i] >= 0.95:
                        icone = "🆗 "
                        delta_cor = 'normal'
                    else:
                        icone = "🔴 "
                        delta_cor = 'inverse'
                    total_trabalhado = float(lista_valor_1[i])
                    percentual_trabalhado = float(lista_valor_2[i])
                    vcol.metric(label=lista_chaves[i],
                                value=('{:,.4}h'.format(total_trabalhado)),
                                delta=icone + ('{:,.2%}'.format(percentual_trabalhado)),
                                delta_color=delta_cor)  # mostra a Metrica de cada Operador

                st.divider()

                # st.markdown('### df_filtrado')
                # st.dataframe(df_filtrado)

                col1, col2 = st.columns(2)
                properties = {'border': '4px solid gray', 'color': 'lawngreen', 'background-color': 'black',
                              'font-size': '16px'}
                # mostrando o dataframe filtrado com as Entradas
                col1.markdown('#### ENTRADAS')
                col1.dataframe(df_entradas.style.set_properties(**properties), hide_index=False,
                               height=35 * len(df_entradas) + 38,
                               column_config={'AnoMes': None, 'Cor': None, 'RegistrouSaida': None, 'Dia': None,
                                              'Hora': None, 'Minuto': None})

                # mostrando o dataframe filtrado com as Entradas
                col2.markdown('#### SAÍDAS')
                col2.dataframe(df_saidas.style.set_properties(**properties), hide_index=False,
                               height=35 * len(df_saidas) + 38,
                               column_config={'AnoMes': None, 'Cor': None, 'RegistrouSaida': None, 'Dia': None,
                                              'Hora': None, 'Minuto': None})

            else:
                fig, ax = plt.subplots(figsize=(8, 5))
                plt.text(0.5, 0.5, "Sem dados para mostrar", fontsize=20, color='red', ha='center', va='center',
                         rotation=30,
                         bbox=dict(facecolor='none', edgecolor='red', linestyle='dashdot', boxstyle='round,pad=1'))
                plt.axis('off')  # Desativar os eixos
                st.pyplot(fig)

        else:
            fig, ax = plt.subplots(figsize=(8, 5))
            plt.text(0.5, 0.5, "O arquivo não apresenta os dados corretos!", fontsize=12, color='red', ha='center',
                     va='bottom', rotation=15,
                     bbox=dict(facecolor='none', edgecolor='red', linestyle='dashdot', boxstyle='round,pad=1'))
            plt.axis('off')  # Desativar os eixos
            st.pyplot(fig)
    elif arq_tipo == 'UnicodeDecodeError':
        fig, ax = plt.subplots(figsize=(8, 5))
        plt.text(0.5, 0.5, "Arquivo danificado (UnicodeDecodeError).\nEntre em contato com o fornecedor.", fontsize=12,
                 color='red', ha='center', va='bottom',
                 rotation=15,
                 bbox=dict(facecolor='none', edgecolor='red', linestyle='dashdot', boxstyle='round,pad=1'))
        plt.axis('off')  # Desativar os eixos
        st.pyplot(fig)

    else:
        fig, ax = plt.subplots(figsize=(8, 5))
        plt.text(0.5, 0.5, "Não foi possível ler o arquivo.\nCertifique-se de escolher o arquivo correto.", fontsize=12,
                 color='red', ha='center', va='bottom',
                 rotation=15,
                 bbox=dict(facecolor='none', edgecolor='red', linestyle='dashdot', boxstyle='round,pad=1'))
        plt.axis('off')  # Desativar os eixos
        st.pyplot(fig)
