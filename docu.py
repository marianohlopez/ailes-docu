import streamlit as st
from dotenv import load_dotenv
from data.connection import get_connection
from logic.filters import filtro_os, filtro_tipos, year_filter
from ui.cards import cant_alum_prest
from ui.cards import porc_alum_dic
from ui.charts import chart_prest_os
from ui.charts import chart_fec_aut
#from ui.charts import chart_fin_aut
from ui.charts import chart_sec_inf

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

st.title("Reporte de Documentación - Año 2025")

# crear conexión
conn = get_connection()

# Obtener OS para el filtro y mostrar selector de OS
os_condition = filtro_os(conn)

# filtro de tipos de prestaciones
tipos_seleccionados = filtro_tipos()

#--- Tarjetas - cant de alumnos y cant de prestaciones
cant_alum_prest(tipos_seleccionados, os_condition, conn)

#--- Tarjeta - Porcentaje de alumnos autorizados hasta diciembre
porc_alum_dic(tipos_seleccionados, os_condition, conn)

#--- Grafico de barras-cant de prestaciones por obra social
chart_prest_os(tipos_seleccionados, os_condition, conn)

# Espacio
st.markdown("<div class='space'></div>", unsafe_allow_html=True)

#--- Filtro de Año

year = st.selectbox("Seleccione el año", ["2025", "2024"])

# Condición de año para la consulta
year_condition = year_filter(year)

# Grafico de linea histórico de activaciones
chart_fec_aut(year_condition, tipos_seleccionados, os_condition, conn)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)

#--- Grafico Fechas de finalizacion de autorizaciones

#chart_fin_aut(os_condition)

# st.markdown("<div class='space'></div>", unsafe_allow_html=True)

#---Filtro de informes



#---Gráfico de informes

chart_sec_inf(os_condition, tipos_seleccionados, conn)

