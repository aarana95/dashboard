import streamlit as st
import functions as ft
import os
import pandas as pd
imagen = 'logo.png'
sheet_name = 'Outcomes_a'

ft.configuracion()
st.write(os.listdir())
good_connect = False
key_file = st.sidebar.file_uploader("Clave:")
actualizar = st.sidebar.button("Actualizar Outcomes")

if actualizar:
    if os.path.isfile("datos_pick"):
        os.remove('datos_pick')

if key_file is not None:

    if not os.path.isfile("datos_pick"):
        key_json = ft.cargar_creadenciales(key_file)
        cliente = ft.connect_to_sheet(key_json)
        worksheet = ft.open_sheet(cliente, sheet_name)
        df = ft.get_df(worksheet)
        df.to_pickle('datos_pick')

    else:
        df = pd.read_pickle('datos_pick')

else:
    st.warning("El archivo con los datos que has cargador no es correcto.")
    st.stop()



menu = st.sidebar.selectbox('Menu:', options=['General', 'Estados de Contratacion', 'Trabajando'])
filtros = ft.opciones_filtros(df)

df = ft.filtrar(df, filtros)

if menu == 'General':
    ft.menu_general(df, imagen)

elif menu == 'Estados de Contratacion':
    ft.menu_contratacion(df)

elif menu == 'Trabajando':

    ft.menu_trabajando(df)