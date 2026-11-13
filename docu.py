import streamlit as st
from dotenv import load_dotenv
from data.connection import get_connection
from data.mongo_db import register
from logic.filters import filtro_os, filtro_tipos, year_filter
from ui.cards import cant_alum_prest, porc_alum_dic
from ui.charts import chart_prest_os, chart_fec_aut, chart_bar_group
from config import DISTRIBUCION_OS


load_dotenv()

st.set_page_config(
    page_title="Dashboard Documentación",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS para las tarjetas
css = open("styles.css").read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Registrar visita una sola vez por día
register(st)

st.title("Indicadores de Documentación - Año 2026")

# crear conexión
conn = get_connection()

# Obtener OS para el filtro y mostrar selector de OS
os_condition = filtro_os(conn)

# filtro de tipos de prestaciones
tipos_seleccionados = filtro_tipos()

#--- Filtro de Año

year = st.selectbox("Seleccione el año", ["Todos los años", "2027", "2026", "2025", "2024"])

# Condición de año para la consulta
year_condition = year_filter(year)

#--- Tarjetas - cant de alumnos y cant de prestaciones
cant_alum_prest(year_condition, tipos_seleccionados, os_condition, conn)

#--- Tarjeta - Porcentaje de alumnos autorizados hasta diciembre
porc_alum_dic(year_condition, tipos_seleccionados, os_condition, conn)

#--- Grafico de barras-cant de prestaciones por obra social
chart_prest_os(year_condition, tipos_seleccionados, os_condition, conn)

# Espacio
st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Grafico de linea histórico de activaciones
chart_fec_aut(tipos_seleccionados, os_condition, conn)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)

chart_bar_group(conn)


