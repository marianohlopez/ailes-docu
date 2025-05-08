import streamlit as st
import plotly.express as px
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

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
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)

# Tarjetas - cant de alumnos y cant de prestaciones

query = """
SELECT 
    COUNT(DISTINCT a.alumno_id) AS cant_alumnos,
    COUNT(DISTINCT p.prestacion_id) AS cant_prestaciones
FROM v_alumnos a 
JOIN v_prestaciones p ON a.alumno_id = p.alumno_id
WHERE p.prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci;
"""

df = pd.read_sql(query, conn)

# Extraer los valores
cant_alumnos = df['cant_alumnos'][0]
cant_prestaciones = df['cant_prestaciones'][0]

# Mostrar en tarjetas
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Cantidad de Alumnos</div>
        <div class="card-value">{cant_alumnos}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Cantidad de Prestaciones</div>
        <div class="card-value">{cant_prestaciones}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Grafico de barras-cant de alumnos por obra social

query2 = """
SELECT o.os_nombre AS obra_social, COUNT(p.prestacion_id) AS cantidad_prestaciones
FROM v_prestaciones p JOIN v_os o 
ON p.prestacion_os = o.os_id
WHERE prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
GROUP BY obra_social
"""
df2 = pd.read_sql(query2, conn)

# Asegurar orden correcto
df2 = df2.sort_values('cantidad_prestaciones', ascending=False)

# Gráfico
fig2 = px.bar(
    df2,
    x='obra_social',
    y='cantidad_prestaciones',
    title='Cantidad de prestaciones por obra social',
    labels={'obra_social': 'Obra Social', 'cantidad_prestaciones': 'Cantidad'},
)

# Ajustar layout para que se use todo el ancho
fig2.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    title_x=0.5,  # Centra el título
    margin=dict(l=150, r=0, t=40, b=20),
    width=1200,
    height=500
)

# Mostrar en Streamlit
st.plotly_chart(fig2, use_container_width=False)