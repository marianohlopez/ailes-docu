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
    <div class="card-container">
        <div class="card">
            <div class="card-title">Cantidad de Alumnos</div>
            <div class="card-value">{cant_alumnos}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card-container">
        <div class="card">
            <div class="card-title">Cantidad de Prestaciones</div>
            <div class="card-value">{cant_prestaciones}</div>
        </div>
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
    text='cantidad_prestaciones'
)

# Ajustar layout para que se use todo el ancho
fig2.update_layout(
    title_x=0.4,  # Centra el título
    height=600
)

# Mostrar en Streamlit
st.plotly_chart(fig2, use_container_width=False)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Tarjeta - Porcentaje de alumnos autorizados hasta diciembre

query3 = """
    SELECT 
        ROUND(
            (SUM(CASE WHEN MONTH(prestacion_fec_aut_OS_hasta) = 12 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
        ) AS porcentaje_diciembre
    FROM 
        v_prestaciones
    WHERE 
        prestacion_estado_descrip = 'ACTIVA' COLLATE utf8mb4_0900_ai_ci
        AND prestacion_fec_aut_OS_hasta IS NOT NULL;
"""

df3 = pd.read_sql(query3, conn)

# Extraer los valores
porc_alumnos_dic = df3['porcentaje_diciembre'][0]

# Mostrar en tarjeta

st.markdown(f"""
    <div class="card-container">
        <div class="card">
            <div class="card-title">Porcentaje de autorizados hasta diciembre</div>
            <div class="card-value">{porc_alumnos_dic} %</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Grafico Fechas de finalizacion de autorizaciones

query4 = """
    SELECT 
        MONTH(prestacion_fec_aut_OS_hasta) AS mes,
        COUNT(*) AS cantidad_prestaciones
    FROM 
        v_prestaciones
    WHERE 
        prestacion_fec_aut_OS_hasta IS NOT NULL
        AND prestacion_estado_descrip = 'ACTIVA' COLLATE utf8mb4_0900_ai_ci
    GROUP BY mes
    ORDER BY mes;
"""

df4 = pd.read_sql(query4, conn)

conn.close()

# Asignar nombres de meses para una visualización más clara
meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
df4['mes'] = df4['mes'].apply(lambda x: meses[x - 1])

fig4 = px.bar(
    df4,
    x='mes',
    y='cantidad_prestaciones',
    title='Fechas de finalización de autorizaciones',
    labels={'mes': 'Mes', 'cantidad_prestaciones': 'Cantidad de Prestaciones'},
    text='cantidad_prestaciones'
)

fig4.update_traces(
    textangle=0  # Forzar el texto en horizontal
)

# Ajustar layout para que se use todo el ancho
fig4.update_layout(
    title_x=0.3,  # Centra el título
)

# Mostrar en Streamlit
st.plotly_chart(fig4, use_container_width=False)




