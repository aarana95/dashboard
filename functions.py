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


# Carga de datos
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
def open_sheet(client, sheet_name, worksheet=0):
    sheet = client.open(sheet_name)
    worksheet = sheet.get_worksheet(worksheet)

    return worksheet
def get_df(worksheet):

    df = pd.DataFrame(worksheet.get_all_records())

    df = df[-df['EMAIL'].isin([''])]
    df.rename(columns={'': 'Nombres'}, inplace=True)

    return(df)


# Menus
def menu_general(df, imagen):
    home(imagen)
    kpi_escuela(df)
    pie_tipos(df)
def menu_contratacion(df):

    st.title("Estados de Contratación")
    kpi_busqueda_empleo(df)

    with st.beta_expander('Opciones:'):
        normalizar = st.checkbox('Normalizar todos los bootcamps.')
        barras = st.checkbox('Barras separadas')


    estado_alumnos(df, 'Estado actual', normalizar, barras)
    estado_alumnos(df, 'Estado 90 días post-graduación', normalizar, barras)
    estado_alumnos(df, 'Estado 180 días post-graduación', normalizar, barras)
def menu_trabajando(df):

    st.title("Alumnos Empleados")

    working = df[df['Fecha Contrataciön'] != '']

    #DEBERIAMOS DE ELIMINAR ESTO CUANDO EL EXCEL ESTE BIEN
    #Inconsistencias en el excel
    working = working[working['Fecha Contrataciön'].apply(lambda x: len(x)) == 10]
    #MdC fue contratada un dia que no existe
    working = working.drop(67)


    fecha_contratacion = pd.to_datetime(working['Fecha Contrataciön'], format='%d/%m/%Y')
    fecha_inicio = pd.to_datetime(working['Promoción'], format='%y.%m')
    working['Dias hasta que encuentra trabajo'] = (fecha_contratacion - fecha_inicio).dt.days


    col1, col2 = st.beta_columns([1, 1])

    #Tiempo de espera vs bootcamp
    with col1:
        fig = px.violin(working, y="Dias hasta que encuentra trabajo", color="Programa", box=True)

        st.header("Tiempo de espera por programa.")
        st.plotly_chart(fig, use_container_width=True)

    #Tiempo de espera vs promocion
    with col2:
        fig = px.violin(working, y="Dias hasta que encuentra trabajo", color="Promoción", box=True)

        st.header("Tiempo de espera por promoción")
        st.plotly_chart(fig, use_container_width=True)


    col1, col2 = st.beta_columns([1, 1])

    with col1:

        with_salary = working[working['Salario Bruto Anual Primera Contratación'] != '']
        with_salary['Salario Bruto Anual Primera Contratación'] = \
            with_salary['Salario Bruto Anual Primera Contratación'].apply(lambda x: x*1000 if x < 100 else x)

        fig = px.scatter(with_salary, x="Dias hasta que encuentra trabajo",
                         y="Salario Bruto Anual Primera Contratación", hover_data=['Nombres'])

        st.header("Salario vs Días para encontrar trabajo")
        st.plotly_chart(fig, use_container_width=True)

    with col2:

        empresas = working['Empresa de primera contratación'].value_counts()[
            working['Empresa de primera contratación'].value_counts() > 1]

        empresas = empresas[empresas.index != ''].sort_values()
        fig = px.bar(y=empresas.index, x=empresas, orientation='h')

        st.header("Empresas que más contratan:")
        st.plotly_chart(fig, use_container_width=True)


# Partes menu general
def home(imagen):
    img = Image.open(imagen)
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

        crear_pie(df, "Programa")

    with col2:

        crear_pie(df, "Promoción")

    with col3:

        crear_pie(df, "Motivación", False)
def crear_pie(df, variable, layout=True):

    st.header(variable)

    var_values = df[variable].value_counts()

    fig = px.pie(names=var_values.index, values=var_values.values)
    fig.update_traces(hoverinfo='label+percent+name')
    fig.update(layout_showlegend=layout)

    st.plotly_chart(fig, use_container_width=True)


# Partes menu contratación
def kpi_busqueda_empleo(df):

    tipo = '3 Continua su búsqueda de trabajo'

    a_180 = kpi_empleo(df, 'Estado 180 días post-graduación', tipo)
    a_90 = kpi_empleo(df, 'Estado 90 días post-graduación', tipo)
    actual = kpi_empleo(df, 'Estado actual', tipo)

    streamlit_metrics.metric_row({
        '% Alumnos que Continuan buscando trabajo':actual,
        '% Alumnos que Continuan buscando trabajo a 90 días de graduarse':a_90,
        '% Alumnos que Continuan buscando trabajo a 180 días de graduarse':a_180
    })
def kpi_empleo(df, momento, type):

    try:
        metr = df.loc[-df[momento].isin(['']), momento].value_counts(normalize=True)[type] * 100
        metr = round(metr, 0)
    except:
        metr = 0

    return metr
def estado_alumnos(df, momento, normalizar, barras):

    barmode = 'relative'
    if barras:
        barmode = 'group'

    progrmas = df.groupby(['Programa', momento])['Nombres'].count()
    progrmas = progrmas.reset_index()
    progrmas = progrmas[(progrmas.iloc[:, 1] != '') & (progrmas.iloc[:, 0] != '')]
    progrmas.sort_values(momento, inplace=True)

    if normalizar:

        progrmas['EMAIL'] /= progrmas.groupby("Programa")["EMAIL"].transform(sum)


    with st.beta_expander(momento, expanded=True):

        fig = px.bar(progrmas, x="Programa", y="Nombres", color=momento,
                      color_discrete_map={'1A Empleado a jornada completa': 'rgb(46, 204, 113)',
                                                        '1B Prácticas a jornada completa': "rgb(46, 204, 113)",
                                                        '1C Contrato temporal o a jornada parcial': "rgb(46, 204, 113)",
                                                        '1D Emprende proyecto propio': 'rgb(46, 204, 113)',
                                                        '2A Empleado en trabajo no relacionado con el bootcamp': 'rgb(241, 196, 15)',
                                                        '2B Continuando con otros estudios': 'rgb(241, 196, 15)',
                                                        '2C No busca trabajo por razones de salud, familiares o personales': 'rgb(241, 196, 15)',
                                                        '3 Continua su búsqueda de trabajo': 'rgb(176, 58, 46)',
                                                        '4 Sin información': 'rgb(33, 47, 60)',
                                                        'Excluido de CIRR': 'rgb(33, 47, 60)'},
                     labels=None, barmode=barmode, hover_data=['Nombres'])


        st.plotly_chart(fig, use_container_width=True)


# Filtros
def opciones_filtros(df):

    with st.sidebar.beta_expander('Filtros:'):

        horario = tipo_filtro(df, 'Horario')
        programa = tipo_filtro(df, 'Programa')
        motivacion = tipo_filtro(df, 'Motivación')
        st.write("funciona?")
        promos = df['Promoción'].unique()
        promos.sort()
        st.write(promos)
        promocion = st.select_slider("Selecciona la promoción que te interesa: ",
                                          options=promos.tolist(),
                                          value=(min(promos), max(promos)))


        isa = st.checkbox("Solo alumnos ISA:")

    return horario, programa, motivacion, promocion, isa
def tipo_filtro(df, tipo):

    filtro_col = ['']
    filtro_col.extend(df[tipo].unique().tolist())
    filtro_col = st.selectbox('Selecciona el ' + tipo + ':', options=filtro_col)

    return filtro_col
def filtrar(df, filtros):

    if filtros[0] != '':
        df = df.loc[df['Horario'] == filtros[0], :]

    if filtros[1] != '':
        df = df.loc[df['Programa'] == filtros[1], :]

    if filtros[2] != '':
        df = df.loc[df['Motivación'] == filtros[2], :]

    if filtros[4]:
        df = df[df['ISA'] != '']

    df = df.loc[(df['Promoción'] >= filtros[3][0]) & (df['Promoción'] <= filtros[3][1]), :]

    return df