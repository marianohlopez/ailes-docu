import streamlit as st
from dotenv import load_dotenv
from data.connection import get_connection
from logic.filters import filtro_os
from logic.filters import filtro_informes
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

# Conexión a la base de datos
conn = get_connection()

# Obtener OS para el filtro y mostrar selector de OS
os_condition = filtro_os(conn)

#--- Tarjetas - cant de alumnos y cant de prestaciones
cant_alum_prest(os_condition, conn)

#--- Tarjeta - Porcentaje de alumnos autorizados hasta diciembre
porc_alum_dic(os_condition, conn)

#--- Grafico de barras-cant de prestaciones por obra social
chart_prest_os(os_condition, conn)

# Espacio
st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Grafico de linea histórico de activaciones
chart_fec_aut(os_condition, conn)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)

#--- Grafico Fechas de finalizacion de autorizaciones

#chart_fin_aut(os_condition)

# st.markdown("<div class='space'></div>", unsafe_allow_html=True)

#---Filtro de informes

tipos_seleccionados = filtro_informes()

#---Gráfico de informes

chart_sec_inf(os_condition, tipos_seleccionados, conn)

