import gspread
import json
import pandas as pd
import plotly.express as px
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import streamlit_metrics
from PIL import Image

def configuracion():
    st.set_page_config(page_title='Dashboard The Bridge', page_icon='https://www.google.com/s2/favicons?domain=www.thebridge.tech', layout="wide")

@st.cache
def cargar_creadenciales(key_file):
    key_file.seek(0)
    key_json = json.load(key_file)

    return key_json

def connect_to_sheet(key_json):


    # Authorize the API
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]

    creds = ServiceAccountCredentials._from_parsed_json_keyfile(key_json, scope)
    client = gspread.authorize(creds)

    return(client)

#@st.cache(hash_funcs={"gspread.client.Client": id})
def open_sheet(client, sheet_name, worksheet=0):
    sheet = client.open(sheet_name)
    worksheet = sheet.get_worksheet(worksheet)

    return worksheet

#@st.cache(hash_funcs={"gspread.models.Worksheet": id})
def get_df(worksheet):

    dataframe = pd.DataFrame(worksheet.get_all_records())
    return(dataframe)

def home():
    img = Image.open('logo.png')
    st.image(img)

def kpi_escuela(df):
    streamlit_metrics.metric_row({
        'Nº Alumnos': df.shape[0],
        'Nº Promociones': len(df['Promoción'].unique()),
        '% Alumnos Graduados': round(df['Estado de matrícula'].value_counts(normalize=True)['Graduado'] * 100, 0),
    })

def pie_tipos(df):
    col1, col2, col3 = st.beta_columns([1, 1, 1])

    with col1:
        st.header("Programa")
        program_values = df['Programa'].value_counts()

        fig = px.pie(names=program_values.index, values=program_values.values)
        fig.update_traces(hoverinfo='label+percent+name')
        # fig.update(layout_showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.header("Promocion")
        program_values = df['Promoción'].value_counts()
        fig = px.pie(names=program_values.index, values=program_values.values)
        fig.update_traces(hoverinfo='label+percent+name')
        # fig.update(layout_showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

#    with col3:
#        st.header("Horario")
#        program_values = df['Horario'].value_counts()
#        fig = px.pie(names=program_values.index, values=program_values.values)
#        fig.update_traces(hoverinfo='label+percent+name')
#        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.header("Motivación")
        program_values = df['Motivación'].value_counts()
        fig = px.pie(names=program_values.index, values=program_values.values)
        fig.update_traces(hoverinfo='label+percent+name')
        fig.update(layout_showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def kpi_busqueda_empleo(df):
    try:
        a_180 = round(df.loc[-df['Estado 180 días post-graduación'].isin(
                ['']), 'Estado 180 días post-graduación'].value_counts(
                normalize=True)['3 Continua su búsqueda de trabajo'] * 100, 0)
    except:
        a_180 = 0

    try:
        a_90 = round(df.loc[-df['Estado 90 días post-graduación'].isin(['']),
                            'Estado 90 días post-graduación'].value_counts(normalize=True)['3 Continua su búsqueda de trabajo'] * 100, 0)

    except:
        a_90=0

    try:
        actual = round(df['Estado actual'].value_counts(normalize=True)['3 Continua su búsqueda de trabajo'] * 100, 0)
    except:
        actual = 0
    streamlit_metrics.metric_row({
        '% Alumnos que Continuan buscando trabajo':
            actual,

        '% Alumnos que Continuan buscando trabajo a 90 días de graduarse':
            a_90,

        '% Alumnos que Continuan buscando trabajo a 180 días de graduarse':
            a_180,

    })

def opciones_filtros(df):

    with st.sidebar.beta_expander('Filtros:'):
        horarios = ['']
        horarios.extend(df['Horario'].unique().tolist())
        horario = st.selectbox(
            'Selecciona formato que te interesa:',
            options=horarios)

        programas = ['']
        programas.extend(df['Programa'].unique().tolist())
        programa = st.selectbox(
            'Selecciona el programa que te interesa:',
            options=programas)


        motivacion = ['']
        motivacion.extend(df['Motivación'].unique().tolist())
        motivacion = st.selectbox(
            'Selecciona la motivación del alumno:',
            options=motivacion)

        promos = df['Promoción'].unique()
        promos.sort()
        promocion = st.select_slider("Selecciona la promoción que te interesa: ",
                                          options=promos.tolist(),
                                          value=(min(promos), max(promos)))


    return horario, programa, motivacion, promocion

def filtrar(df, filtros):

    if filtros[0] != '':
        df = df.loc[df['Horario'] == filtros[0], :]

    if filtros[1] != '':
        df = df.loc[df['Programa'] == filtros[1], :]

    if filtros[2] != '':
        df = df.loc[df['Motivación'] == filtros[2], :]


    df = df.loc[(df['Promoción'] >= filtros[3][0]) & (df['Promoción'] <= filtros[3][1]), :]

    return df

def estado_alumnos(df, momento, normalizar, barras):

    barmode = 'relative'
    dd2 = df.groupby(['Programa', momento])['EMAIL'].count()
    dd2 = dd2.reset_index()
    dd2 = dd2[(dd2.iloc[:, 1] != '') & (dd2.iloc[:, 0] != '')]

    if barras:
        barmode = 'group'


    #No me siento orgulloso de este código
    if normalizar:
        total_programa = dd2.groupby('Programa')['EMAIL'].sum()
        for i in range(len(total_programa)):
            dd2.loc[dd2["Programa"] == total_programa.index[i], 'EMAIL'] = dd2.loc[dd2["Programa"] == total_programa.index[
                i], 'EMAIL'] / total_programa[i]


    fig = px.bar(x=dd2["Programa"], y=dd2["EMAIL"], color=dd2[momento],
                  color_discrete_map={'1A Empleado a jornada completa': 'rgb(46, 204, 113)',
                                                    '1B Prácticas a jornada completa': "rgb(22, 160, 133)",
                                                    '1C Contrato temporal o a jornada parcial': "rgb(130, 224, 170)",
                                                    '1D Emprende proyecto propio': 'rgb(88, 214, 141)',
                                                    '2A Empleado en trabajo no relacionado con el bootcamp': 'rgb(241, 196, 15)',
                                                    '2B Continuando con otros estudios': 'rgb(52, 152, 219)',
                                                    '2C No busca trabajo por razones de salud, familiares o personales': 'rgb(95, 106, 106)',
                                                    '3 Continua su búsqueda de trabajo': 'rgb(176, 58, 46)',
                                                    '4 Sin información': 'rgb(33, 47, 60)',
                                                    'Excluido de CIRR': 'rgb(27, 38, 49)'},
                 labels=None, barmode=barmode)

    st.plotly_chart(fig, use_container_width=True)


