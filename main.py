import streamlit as st
import functions as ft

csv_path = 'Outcomes'

ft.configuracion()

good_connect = False

key_file = st.sidebar.file_uploader("Clave:")

if key_file is not None:
    key_json = ft.cargar_creadenciales(key_file)
    cliente = ft.connect_to_sheet(key_json)
    good_connect = True


if not good_connect:
    st.warning("El archivo con los datos que has cargador no es correcto.")
    st.stop()


sheet_name = 'Outcomes_a'

worksheet = ft.open_sheet(cliente, sheet_name)


df = ft.get_df(worksheet)
df = df[-df['EMAIL'].isin([''])]


menu = st.sidebar.selectbox('Menu:', options=['General', 'Estados de Contratacion'])

filtros = ft.opciones_filtros(df)

df = ft.filtrar(df, filtros)

if menu == 'General':
    ft.home()
    ft.kpi_escuela(df)
    ft.pie_tipos(df)

elif menu == 'Estados de Contratacion':

    ft.kpi_busqueda_empleo(df)

    with st.beta_expander('Opciones:'):
        normalizar = st.checkbox('Normalizar todos los bootcamps.')
        barras = st.checkbox('Barras separadas')

    with st.beta_expander('Estado actual', expanded=True):
        ft.estado_alumnos(df, 'Estado actual', normalizar, barras)

    with st.beta_expander('Estado 90 días post-graduación', expanded=True):
        ft.estado_alumnos(df, 'Estado 90 días post-graduación', normalizar, barras)

    with st.beta_expander('Estado 180 días post-graduación', expanded=True):
        ft.estado_alumnos(df, 'Estado 180 días post-graduación', normalizar, barras)
