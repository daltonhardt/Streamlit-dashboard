############################
#   NIDEC RFID DASHBOARD   #
#   Author: Dalton Hardt   #
#   Date:  Jan/24          #
############################

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta

# Para mostrar todas as linhas e colunas do Dataframe
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('max_colwidth', 25)

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

# Configurar o idioma para português
# locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Substitua 'pt_BR.UTF-8' pelo locale do seu sistema


# Definindo lista com 24 cores para definir os Operadores
cores = ['coral', 'limegreen', 'dodgerblue', 'yellow', 'orange', 'deepskyblue', 'pink', 'lightsalmon',
         'cyan', 'magenta', 'lime', 'gold', 'silver', 'beige', 'khaki', 'turquoise',
         'lavender', 'whitesmoke', 'palegreen', 'lightsteelblue', 'aquamarine', 'tomato', 'lightgray', 'tan']

# Definindo um dataframe com a lista de cores
df_cores = pd.DataFrame(cores, columns=['Cor'])

# Iniciando o streamlit
st.set_page_config(page_title="RFID Dashboard", page_icon="✅", layout="wide")
st.image('./logoNidec.png')
# st.image('/Users/dalton/Desktop/workspace/figuras/logoNidec.png')
st.title("RFID Itaiópolis Dashboard")

# Lendo o arquivo CSV
arquivo = st.sidebar.file_uploader('Escolha o arquivo (.csv)', type='csv')
if arquivo is not None:
    df = pd.read_csv(arquivo)  # lendo o arquivo e transformando em um Dataframe Pandas

    # ajustando algumas colunas
    df['Data'] = pd.to_datetime(df["Data"], dayfirst=True)
    df['AnoMes'] = df["Data"].apply(lambda x: str(x.month) + "-" + str(x.year))  # criando coluna Mes-Ano
    df['Dia'] = df['Data'].dt.strftime('%d').astype(int)  # criando a coluna somente com o dia do mês
    df['Hora'] = df['Data'].dt.strftime('%H:%M')  # criando a coluna somente com Hora e Minuto do dia

    # associando as cores unicas para cada Operador
    operadores = df['Nome'].unique()  # criando lista com os nomes dos Operadores
    df_operadores = pd.DataFrame(operadores, columns=['NomeOperador'])  # criando um dataframe
    df_operador_cor = pd.merge(df_operadores, df_cores, left_index=True, right_index=True)  # mesclando os dataframes
    # print(df_operador_cor)
    # adicionando as cores ao dataframe original
    df = pd.merge(df, df_operador_cor, left_on='Nome', right_on='NomeOperador',
                  how='inner').sort_values(by='Data', ascending=True).reset_index(drop=True)

    # ajustando algumas colunas
    df = df.drop(columns=['Matricula'])  # Deletando a coluna Matricula
    df = df.drop(columns=['NomeOperador'])  # Deletando a coluna Matricula
    df = df.drop_duplicates()  # Retirando as linhas duplicadas
    df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)  # removendo espaço das colunas string (object)

    # Criando um SelectBox para selecionar o Ano e o Mes como chave de busca
    st.sidebar.header('Escolha os filtros:')
    var_ano_mes = st.sidebar.selectbox("Selecione o Mês e Ano", df['AnoMes'].drop_duplicates())
    # Criando um SelectBox para selecionar o Posto de Trabalho como chave de busca
    var_posto = st.sidebar.selectbox("Selecione o Posto de Trabalho", df["Posto"].drop_duplicates().sort_values())
    # Criando um CheckBox para marcar se quer Todos Operadores ou não
    var_todos_operadores = st.sidebar.checkbox("Todos Operadores", value=True)

    # filtra o Dataframe com o Ano-Mes e Posto escolhidos, inicialmente com Todos os nomes de Operadores
    df_filtrado = df[(df['AnoMes'] == var_ano_mes) & (df['Posto'] == var_posto) &
                     (df['Evento'].isin([2, 3]))].sort_values(by='Data', ascending=True).reset_index(drop=True)
    # print('df_filtrado:\n', df_filtrado)

    df_filtrado['RegistrouSaida'] = df_filtrado['Nome'].eq(
        df_filtrado['Nome'].shift(-1))  # True/False so o Operador marcou a saida do Posto
    df_filtrado['RegistrouSaida'].replace(True, 'Sim', inplace=True)  # substituindo True por Sim
    df_filtrado['RegistrouSaida'].replace(False, 'Nao', inplace=True)  # substituindo False por Nao
    df_filtrado.loc[(df_filtrado['Evento'] == 3), 'RegistrouSaida'] = '-'  # substituindo as saidas por '-'
    df_filtrado = df_filtrado.reset_index(drop=True)  # resetando o indíce do dataframe

    # criando um dataframe somente com os eventos de ENTRADA (=2)
    df_entradas = df_filtrado[(df_filtrado['Evento'] == 2)].reset_index(drop=True)
    # print('df_entradas:\n', df_entradas)

    # criando um dataframe somente com os eventos de SAIDA (=3)
    df_saidas = df_filtrado[(df_filtrado['Evento'] == 3)].reset_index(drop=True)
    # print('df_saidas:\n', df_saidas)

    # Pegando o Primeiro e o ultimo dia do mês selecionado
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
        if dia[0] in ('Seg', 'Ter', 'Qua', 'Qui', 'Sex'):
            horas_disponiveis += horas_dia_semana
        else:
            horas_disponiveis += horas_dia_sabado
    # print('Horas disponiveis.......', horas_disponiveis)
    # Calculando as horas de trabalho disponiveis no periodo selecionado
    # for number in range(first_day_month, last_day_month+1):
    #    print(number)
    for i, dia in enumerate(datas_eventos):
        # print('Loop dia   i    ', dia)
        # Usar strftime para obter o nome do dia da semana
        dia_semana = dia.strftime('%a')
        dia_mes = dia.strftime('%d')
        hora_dia = dia.strftime('%H')
        # print("- Dia da semana ", i, ": ", dia_semana)
        # print("- Dia do mes: ", i, ": ", dia_mes)
        # print("- Hora do dia: ", i, ": ", hora_dia)

        if dia_semana == 'Sab' and hora_dia in ('05', '06', '07', '08'):
            hora_entrada = dia.strftime('%Y-%m-%d 05:00:00')
            hora_saida = dia.strftime('%Y-%m-%d 09:00:00')
            # horas_disponiveis = horas_disponiveis + horas_dia_sabado
            # print('1.hora entrada:', hora_entrada, '  1.hora_saida: ', hora_saida)
        elif dia_semana == 'Sab' and hora_dia in ('09', '10', '11', '12'):
            hora_entrada = dia.strftime('%Y-%m-%d 09:00:00')
            hora_saida = dia.strftime('%Y-%m-%d 13:00:00')
            # horas_disponiveis = horas_disponiveis + horas_dia_sabado
            # print('2.hora entrada:', hora_entrada, '  2.hora_saida: ', hora_saida)
        elif dia_semana in ('Seg', 'Ter', 'Qua', 'Qui', 'Sex') and hora_dia in (
                '05', '06', '07', '08', '09', '10', '11', '12', '13'):
            hora_entrada = dia.strftime('%Y-%m-%d 05:00:00')
            hora_saida = dia.strftime('%Y-%m-%d 13:30:00')
            # horas_disponiveis = horas_disponiveis + horas_dia_semana
            # print('3.hora entrada:', hora_entrada, '  3. hora_saida: ', hora_saida)
        else:
            hora_entrada = dia.strftime('%Y-%m-%d 13:30:00')
            hora_saida = dia.strftime('%Y-%m-%d 22:00:00')
            # horas_disponiveis = horas_disponiveis + horas_dia_semana
            # print('4.hora entrada:', hora_entrada, '  4. hora_saida: ', hora_saida)

    print('TOTAL horas disponiveis no periodo =', horas_disponiveis)

    # Tratando os casos em que o Operador não deu saida no seu posto de trabalho:
    # comparando os dataframes, linha a linha, para saber se o Nome no dataframe de saida é diferente do Nome
    # no dataframe de entrada. Se for diferente, substitui o Nome no dataframe de saida pelo nome
    for (index1, row1), (index2, row2) in zip(df_entradas.iterrows(), df_saidas.iterrows()):
        if row2['Nome'] != row1['Nome']:
            df_saidas.replace(row2['Nome'], row1['Nome'], inplace=True)

    if var_todos_operadores:  # se o checkBox estiver marcado com TODOS Operadores
        # operadores = df_entradas['Nome'].unique()  # pega os nomes unicos do dataframe
        df_operadores = df_entradas.drop_duplicates(subset=['Nome', 'Cor'])
        lista_operadores = df_operadores[['Nome', 'Cor']].values.tolist()
    else:
        seleciona_operador = df_entradas['Nome'].unique()  # cria variavel com o nome do operador selecionado
        var_operador = st.sidebar.selectbox("Selecione o Operador",
                                            seleciona_operador)  # cria o selecctbox já com o operador selecionado
        # filtra o Dataframe com o Ano-Mes e Posto escolhidos e com o nome do Operador selecionado
        df_entradas = df_entradas[(df_entradas['AnoMes'] == var_ano_mes) & (df_entradas['Posto'] == var_posto) &
                                  (df_entradas['Nome'] == var_operador)].sort_values(by='Data',
                                                                                     ascending=True).reset_index(
            drop=True)
        df_saidas = df_saidas[(df_saidas['AnoMes'] == var_ano_mes) & (df_saidas['Posto'] == var_posto) &
                              (df_saidas['Nome'] == var_operador)].sort_values(by='Data',
                                                                               ascending=True).reset_index(
            drop=True)
        # print('var_operador =', var_operador)
        # print('df_entradas:\n', df_entradas)
        # print('df_saidas:\n', df_saidas)
        # print('df_filtrado: \n', df_filtrado['Nome'].str.strip() == var_operador)
        df_operadores = df_entradas.loc[df_entradas['Nome'].str.strip() == var_operador].reset_index(drop=True)
        # print('df_operadores: \n', df_operadores)
        df_operadores = df_operadores.drop_duplicates(subset=['Nome', 'Cor'], keep='first').reset_index(drop=True)
        # print('df_operadores..: \n', df_operadores)
        lista_operadores = df_operadores[['Nome', 'Cor']].values.tolist()

    # print('df_entradas:\n', df_entradas)
    # print('df_saidas:\n', df_saidas)
    # print('lista de operadores: ', lista_operadores)

    # criando um dicionário a partir da lista de operadores para armazenar as horas de trabalho de cada operador
    lista = []
    for i in range(len(lista_operadores)):
        item = str(lista_operadores[i][0])
        item = item.replace(" ", "")
        lista.append(item)

    contador_horas = dict.fromkeys(lista, [0.0, 0.0])
    # print('Iniciando o dicionario contador de horas...:\n', contador_horas)

    df_entradas['Data'] = pd.to_datetime(df_entradas["Data"], dayfirst=False)
    df_entradas['Data'] = df_entradas['Data'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # criando um dataframe somente com os eventos de saida (=3)
    # df_saidas = df_filtrado[(df_filtrado['Evento'] == 3)].reset_index(drop=True)
    df_saidas.drop('RegistrouSaida', axis=1, inplace=True)
    df_saidas['Data'] = pd.to_datetime(df_saidas["Data"], dayfirst=False)
    df_saidas['Data'] = df_saidas['Data'].dt.strftime('%Y-%m-%d %H:%M:%S')

    if not df_entradas.empty:
        # definindo as listas com datas de entrada e saida e formatando para '%Y-%m-%d %H:%M:%S'
        datas_entradas = df_entradas['Data'].tolist()
        inicio_dia = datas_entradas[0]
        inicio_dia = datetime.strptime(inicio_dia, '%Y-%m-%d %H:%M:%S')
        inicio_dia = inicio_dia.replace(day=1, hour=5, minute=0)
        fim_dia = inicio_dia.replace(day=1, hour=22, minute=0)

        datas_entradas = [datetime.strptime(data, '%Y-%m-%d %H:%M:%S') for data in datas_entradas]

        datas_saidas = df_saidas['Data'].tolist()
        datas_saidas = [datetime.strptime(data, '%Y-%m-%d %H:%M:%S') for data in datas_saidas]

        # Criando uma lista de datas com espaçamentos de uma hora entre 05:00 e 22:00
        entrada = datetime.strptime(df_entradas['Data'][0], '%Y-%m-%d %H:%M:%S')
        mes = entrada.strftime('%m')
        ano = entrada.strftime('%Y')
        data_inicial = datetime(int(ano), int(mes), 1, 5, 0, 0)  # Data inicial: ano, mês, dia, hora, minuto, segundo
        espacamento = timedelta(hours=1)  # Espaçamento de 1 hora
        num_horas = 18  # Número de horas entre as 5:00 e as 22:00
        lista_de_horas = [data_inicial + i * espacamento for i in range(num_horas)]  # gerando a lista

        fig, ax = plt.subplots(figsize=(8, 5))
        # print('lista_operadores:', lista_operadores)

        # criando as linhas do gráfico
        duracao = 0
        for (index1, row1), (index2, row2) in zip(df_entradas.iterrows(), df_saidas.iterrows()):
            entrada = datetime.strptime(row1['Data'], '%Y-%m-%d %H:%M:%S')
            dia = entrada.strftime('%d')
            entrada = entrada.replace(day=1)

            saida = datetime.strptime(row2['Data'], '%Y-%m-%d %H:%M:%S')
            saida = saida.replace(day=1)

            pessoa = row1['Nome']
            # print('duracao=', duracao)
            duracao = round(((saida - entrada).total_seconds() / 3600), 2)  # convertendo para horas
            print(pessoa, 'no dia', dia, 'entrou às', row1['Hora'], 'e saiu às', row2['Hora'], ' [', duracao, ']')

            nome = row1['Nome'].replace(" ", "")
            for key in contador_horas.keys():
                # print('key:', key, 'nome:', nome)
                if key == nome:
                    contador_horas[key] = contador_horas[key].copy()  # IMPORTANTE para não propagar para outras chaves
                    contador_horas[key][0] = contador_horas[key][0] + duracao
                    contador_horas[key][1] = contador_horas[key][0] / horas_disponiveis
                    # print(contador_horas[key], '', contador_horas[key][0])
                    duracao = 0

            # criando as linhas horizontais
            ax.hlines(dia, entrada, saida, color=row1['Cor'], linewidth=20, label=row1['Nome'])
            # Adicionando texto com a duração e posicionando próximo
            ax.text(saida, dia, f'{duracao:.2f}h', verticalalignment='center', horizontalalignment='right', fontsize=8)

        plt.legend()
        linhas_legenda = []
        for item in lista_operadores:
            linha, = ax.plot([], [], label=item[0], color=item[1], linewidth=12)
            linhas_legenda.append(linha)
        ax.legend(handles=linhas_legenda, loc='upper left', bbox_to_anchor=(1, 1))

        # Adicionando rótulos e título
        ax.set_xlabel('Hora')
        ax.set_ylabel('Dia')
        plt.xticks(rotation=90)

        lims = (inicio_dia, fim_dia)
        locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.set_xlim(lims)

        ax.grid(True)  # ativando o grid
        ax.grid(axis='x', which="major", linewidth=1)  # customizando grid Maior somente no eixo X
        ax.grid(axis='x', which="minor", linewidth=0.5, alpha=0.25)  # customizando o grid Menor somente no eixo X
        ax.minorticks_on()  # ativando os ticks menores
        ax.yaxis.set_tick_params(which='minor', bottom=False)  # desativando os ticks menores no eixo Y
        ax.tick_params(axis='x', direction='out', length=13, width=2)  # customizando os ticks no eixo X

        plt.title(f'Operadores no Posto de Trabalho {var_posto} em {var_ano_mes}', pad=5, fontsize=12,
                  fontweight='bold')

        st.pyplot(fig)
        # print('DICIONARIO contador_horas:', contador_horas)
        contador_horas_v1 = {k: round(v[0], 2) for k, v in contador_horas.items()}
        contador_horas_v1 = dict(sorted(contador_horas_v1.items()))
        print('dicionario contador de horas PRIMEIRO VALOR:\n', contador_horas_v1)

        contador_horas_v2 = {k: round(v[1], 4) for k, v in contador_horas.items()}
        contador_horas_v2 = dict(sorted(contador_horas_v2.items()))
        print('dicionario contador de horas SEGUNDO VALOR:\n', contador_horas_v2)

        # criando e mostrando as METRICAS de horas de cada Operador
        st.markdown('''---''')
        st.markdown('### Total de Horas do Operador dentro do periodo selecionado:')
        st.markdown(
                    '''
                    <style>
                    [data-testid="stMetricDelta"] svg {
                        transform: rotate(90deg);
                    }
                    </style>
                    ''', unsafe_allow_html=True)

        lista_chaves = list(contador_horas_v1.keys())
        lista_valor_1 = list(contador_horas_v1.values())
        lista_valor_2 = list(contador_horas_v2.values())
        col_list = st.columns(len(lista_chaves))  # criando o numero de colunas de acordo com o numero de Operadores
        for i, vcol in enumerate(col_list):
            if lista_valor_2[i] >= 0.95:
                delta_cor = 'normal'
            else:
                delta_cor = 'inverse'

            vcol.metric(label=lista_chaves[i],
                        value=('{:,.2}h'.format(float(lista_valor_1[i]))),
                        delta=('{:,.2%}'.format(float(lista_valor_2[i]))),
                        delta_color=delta_cor)  # mostra a Metrica de cada Operador

        st.markdown('''---''')

        col1, col2 = st.columns(2)
        properties = {'border': '4px solid gray', 'color': 'lawngreen', 'background-color': 'black',
                      'font-size': '16px'}
        # mostrando o dataframe filtrado com as Entradas
        col1.markdown('#### Entradas')
        col1.dataframe(df_entradas.style.set_properties(**properties), hide_index=True,
                       column_config={'AnoMes': None, 'Evento': None, 'Cor': None, 'RegistrouSaida': None})

        # mostrando o dataframe filtrado com as Entradas
        col2.markdown('#### Saídas')
        col2.dataframe(df_saidas.style.set_properties(**properties), hide_index=True,
                       column_config={'AnoMes': None, 'Evento': None, 'Cor': None, 'RegistrouSaida': None})

    else:
        fig, ax = plt.subplots(figsize=(8, 5))
        plt.text(0.5, 0.5, "Sem dados para mostrar", fontsize=20, color='red', ha='center', va='center', rotation=30,
                 bbox=dict(facecolor='none', edgecolor='red', linestyle='dashdot', boxstyle='round,pad=1'))
        plt.axis('off')  # Desativar os eixos
        st.pyplot(fig)
