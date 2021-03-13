import streamlit as st
import functions as ft

imagen = 'logo.png'
sheet_name = 'Outcomes_a'

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

worksheet = ft.open_sheet(cliente, sheet_name)


df = ft.get_df(worksheet)


menu = st.sidebar.selectbox('Menu:', options=['General', 'Estados de Contratacion', 'Trabajando'])
filtros = ft.opciones_filtros(df)

df = ft.filtrar(df, filtros)

if menu == 'General':
    ft.menu_general(df, imagen)

elif menu == 'Estados de Contratacion':
    ft.menu_contratacion(df)

elif menu == 'Trabajando':

    ft.menu_trabajando(df)