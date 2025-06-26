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

# Obtener OS para el filtro

q_os = """ 
    SELECT o.os_nombre
    FROM v_os o JOIN v_prestaciones p
    ON o.os_id = p.prestacion_os
    WHERE p.prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
	AND p.prestacion_id >= 1
 """

df_os = pd.read_sql(q_os, conn)

obras_sociales = ['Todas las os'] + list(df_os['os_nombre'].unique())

# Selector en Streamlit
selected_os = st.selectbox("Seleccione una obra social:", obras_sociales)

# Condición de os en la consulta
os_condition = ""
if selected_os != "Todas las os":
    os_condition = f"AND o.os_nombre = '{selected_os}'"


# Tarjetas - cant de alumnos y cant de prestaciones

def prest_alum(c1, c2):
    q_prest_alum = f"""
    SELECT 
        COUNT(DISTINCT a.alumno_id) AS cant_alumnos,
        COUNT(DISTINCT p.prestacion_id) AS cant_prestaciones
    FROM 
        v_os o
    JOIN 
        v_prestaciones p ON p.prestacion_os = o.os_id
    JOIN 
        v_alumnos a ON p.alumno_id = a.alumno_id
    WHERE 
        p.prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
    {c1}
    {c2}
    """
    df_prest_alum = pd.read_sql(q_prest_alum, conn)

    # Extraer los valores
    cant_alumnos = df_prest_alum['cant_alumnos'][0]
    cant_prestaciones = df_prest_alum['cant_prestaciones'][0]

    return cant_alumnos, cant_prestaciones


cant_alumnos, cant_prestaciones = prest_alum(os_condition, "")

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


# Tarjeta - Porcentaje de alumnos autorizados hasta diciembre

q_alum_aut = f"""
    SELECT 
        ROUND(
            (SUM(CASE WHEN MONTH(p.prestacion_fec_aut_OS_hasta) = 12 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
        ) AS porcentaje_diciembre
    FROM 
        v_prestaciones p
    JOIN 
        v_os o ON p.prestacion_os = o.os_id
    WHERE 
        prestacion_estado_descrip = 'ACTIVA' COLLATE utf8mb4_0900_ai_ci
        AND prestacion_fec_aut_OS_hasta IS NOT NULL
        {os_condition};
"""

df_alum_aut = pd.read_sql(q_alum_aut, conn)

# Extraer los valores
porc_alumnos_dic = df_alum_aut['porcentaje_diciembre'][0]

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

# Grafico de barras-cant de prestaciones por obra social

q_alum_os = f"""
    SELECT o.os_nombre AS obra_social, COUNT(p.prestacion_id) AS cantidad_prestaciones
    FROM v_prestaciones p JOIN v_os o 
    ON p.prestacion_os = o.os_id
    WHERE prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
    {os_condition}
    GROUP BY obra_social;
"""
df_alum_os = pd.read_sql(q_alum_os, conn)

# Asegurar orden correcto
df_alum_os = df_alum_os.sort_values('cantidad_prestaciones', ascending=False)

# Gráfico
fig_alum_os = px.bar(
    df_alum_os,
    x='obra_social',
    y='cantidad_prestaciones',
    title='Cantidad de prestaciones por obra social',
    labels={'obra_social': 'Obra Social', 'cantidad_prestaciones': 'Cantidad'},
    text='cantidad_prestaciones'
)

fig_alum_os.update_xaxes(
    tickangle=-45  # Forzar el texto en horizontal
)

# Ajustar layout

fig_alum_os.update_layout(
    title_x=0.4,  # Centra el título
    height=600,
    width=2000,
    margin=dict(l=40, r=40, t=80, b=120)
)

# Mostrar en Streamlit
st.plotly_chart(fig_alum_os, use_container_width=False)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Grafico de linea histórico de activaciones

q_fec_aut = f"""
SELECT o.os_nombre, p.prestacion_fec_aut_os
    FROM v_prestaciones p JOIN v_os o 
    ON p.prestacion_os = o.os_id
    WHERE prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
    {os_condition}
"""

df_fec_aut = pd.read_sql(q_fec_aut, conn)

print(df_fec_aut.columns.tolist())
print(df_fec_aut.head(3))


df_fec_aut["prestacion_fec_aut_OS"] = pd.to_datetime(df_fec_aut["prestacion_fec_aut_OS"])


df_fec_aut["year_month"] = df_fec_aut["prestacion_fec_aut_OS"].dt.to_period("M").dt.to_timestamp()

# Conteo de prestaciones por mes
serie = (
    df_fec_aut.groupby("year_month", as_index=False)
      .size()                         
      .rename(columns={"size": "prestaciones"})
      .sort_values("year_month")
)


full_range = pd.date_range(
    serie["year_month"].min(), serie["year_month"].max(), freq="MS"
)
serie = (
    serie.set_index("year_month")
          .reindex(full_range, fill_value=0)
          .rename_axis("year_month")
          .reset_index()
)

serie["prestaciones_acum"] = serie["prestaciones"].cumsum()

fig = px.line(
    serie,
    x="year_month",
    y="prestaciones_acum",
    markers=True,               
    labels={
        "year_month": "Mes",
        "prestaciones_acum": "Cantidad de prestaciones activas"
    },
    title=f"Histórico - Prestaciones activas por mes 2025"
)

fig.update_layout(
    xaxis=dict(dtick="M1", tickformat="%Y-%m"),
    title_x=0.4
    )

st.plotly_chart(fig, use_container_width=True)

st.markdown("<div class='space'></div>", unsafe_allow_html=True)


# Grafico Fechas de finalizacion de autorizaciones

q_fec_aut = f"""
    SELECT 
        MONTH(p.prestacion_fec_aut_OS_hasta) AS mes,
        COUNT(*) AS cantidad_prestaciones
    FROM 
        v_prestaciones p
    JOIN 
        v_os o ON p.prestacion_os = o.os_id
    WHERE 
        p.prestacion_fec_aut_OS_hasta IS NOT NULL
        AND p.prestacion_estado_descrip = 'ACTIVA' COLLATE utf8mb4_0900_ai_ci
        {os_condition}
    GROUP BY mes
    ORDER BY mes;
"""

df_fec_aut = pd.read_sql(q_fec_aut, conn)

# Asignar nombres de meses para una visualización más clara
meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
df_fec_aut['mes'] = df_fec_aut['mes'].apply(lambda x: meses[x - 1])

fig_fec_aut = px.bar(
    df_fec_aut,
    x='mes',
    y='cantidad_prestaciones',
    title='Fechas de finalización de autorizaciones',
    labels={'mes': 'Mes', 'cantidad_prestaciones': 'Cantidad de Prestaciones'},
    text='cantidad_prestaciones'
)

fig_fec_aut.update_traces(
    textangle=0.5  # Forzar el texto en horizontal
)

# Ajustar layout
fig_fec_aut.update_layout(
    title_x=0.3,  # Centra el título
)

# Mostrar en Streamlit
# st.plotly_chart(fig_fec_aut, use_container_width=False)

# st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Filtro para informes

tipos_informe = ['SAIE', 'MA-APOYO', 'TERAPIAS', 'AT']

tipos_seleccionados = st.multiselect(
    'Selecciona los tipos de prestación:',
    options=tipos_informe,
    default=tipos_informe,
)

if tipos_seleccionados:
    filtro_informes = "AND p.prestipo_nombre_corto IN ({})".format(
        ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
    )
else:
    filtro_informes = "AND p.prestipo_nombre_corto IN ('')"

col1, col2 = st.columns([8, 2])

cant_alumnos_inf, _ = prest_alum(os_condition, filtro_informes)

with col2:
    st.markdown(f"""
    <div class="card-container">
        <div class="card">
            <div class="card-title">Cantidad de Alumnos</div>
            <div class="card-value">{cant_alumnos_inf}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Grafico de barras con informes de alumnos

q_alumno_inf = f"""
    SELECT 
        i.informecat_nombre AS categoria,
        COUNT(DISTINCT i.alumno_id) AS cantidad_alumnos
    FROM 
        v_informes i 
    JOIN 
        v_prestaciones p ON i.alumno_id = p.alumno_id
    JOIN
        v_os o ON p.prestacion_os = o.os_id
    WHERE 
        (YEAR(i.fec_carga) = 2025 
        OR i.informecat_nombre = 'Informe Inicial - ADMISIÓN'
        OR i.informecat_nombre = 'Otro')
    AND
        p.prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
    {filtro_informes}
    {os_condition}
    GROUP BY 
        i.informecat_nombre
    ORDER BY 
        cantidad_alumnos DESC;
"""

# Cargar los datos en un DataFrame
df_alumno_inf = pd.read_sql(q_alumno_inf, conn)

# Crear el gráfico
fig_alum_inf = px.bar(
    df_alumno_inf,
    x='categoria',
    y='cantidad_alumnos',
    title='Cantidad de alumnos por informe',
    labels={'categoria': 'Categoría',
            'cantidad_alumnos': 'Cantidad de alumnos'},
    text='cantidad_alumnos'
)

# Ajustes del gráfico
fig_alum_inf.update_xaxes(tickangle=-45)
fig_alum_inf.update_layout(title_x=0.5)

with col1:
    st.plotly_chart(fig_alum_inf, use_container_width=False)

conn.close()
