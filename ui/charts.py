import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from ui.cards import card_alumnos_inf
from data.queries import q_alum_os
from data.queries import q_fec_aut
from data.queries import q_fin_aut
from data.queries import q_prest_alum
from data.queries import q_alumno_inf


#--- Grafico de barras-cant de prestaciones por obra social

def chart_prest_os(tipos_seleccionados, os_condition, conn):
  
  if tipos_seleccionados:
      filtro_tipos = "AND p.prestipo_nombre_corto IN ({})".format(
              ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
          )
  else:
      filtro_tipos = "AND p.prestipo_nombre_corto IN ('')"

  df_alum_os = q_alum_os(os_condition, filtro_tipos, conn)

  # Gráfico
  fig_alum_os = px.bar(
      df_alum_os,
      x='obra_social',
      y='cantidad_prestaciones',
      title='Cantidad de prestaciones por obra social',
      labels={'obra_social': 'Obra Social', 'cantidad_prestaciones': 'Cantidad'},
      text='cantidad_prestaciones'
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


#--- Grafico de linea histórico de activaciones

def chart_fec_aut(year_condition, tipos_seleccionados, os_condition, conn):
  
    if tipos_seleccionados:
        filtro_tipos = "AND p.prestipo_nombre_corto IN ({})".format(
                ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
            )
    else:
        filtro_tipos = "AND p.prestipo_nombre_corto IN ('')"
  

    df = q_fec_aut(year_condition, filtro_tipos, os_condition, conn)

    initial_balance = 0

    # acumulados
    df["bajas_acum"] = df["cant_bajas"].cumsum()
    df["altas_acum"] = initial_balance + (df["cant_altas"] - df["cant_bajas"]).cumsum()

    fig = px.line(
        df,
        x="periodo",
        y=["bajas_acum", "altas_acum"],
        title="Evolución de altas y bajas",
        labels={
            "value": "Cantidad acumulada",
            "periodo": "Periodo",
            "altas_acum": "Altas (acum)",
            "bajas_acum": "Bajas (acum)",
        },
        color_discrete_map={
            "altas_acum": "green",
            "bajas_acum": "red",
        },
        markers=True,
        custom_data=["cant_altas", "cant_bajas"]
    )

    # hovertemplate para mostrar custom_data
    fig.update_traces(
        hovertemplate=
        "Periodo: %{x}<br>" +
        "Cantidad acumulada: %{y}<br>" +
        "Altas del mes: %{customdata[0]}<br>" +
        "Bajas del mes: %{customdata[1]}"
    )

    # layout
    fig.update_layout(
        xaxis_title="Periodo",
        yaxis_title="Cantidad acumulada",
        legend_title="Serie",
        title_x=0.5,
        height=420
    )

    fig.update_xaxes(type="category")

    # mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)


# Grafico Fechas de finalizacion de autorizaciones

def chart_fin_aut(conn, os_condition):   

  df_fec_aut = q_fin_aut(os_condition, conn)

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
  st.plotly_chart(fig_fec_aut, use_container_width=False)


#--- Sección de informes

def chart_sec_inf(os_condition,tipos_seleccionados, conn):

    if tipos_seleccionados:
        filtro_tipos = "AND p.prestipo_nombre_corto IN ({})".format(
                ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
            )
    else:
        filtro_tipos = "AND p.prestipo_nombre_corto IN ('')"

    col1, col2 = st.columns([8, 2])

    cant_alumnos_inf, _ = q_prest_alum(os_condition, filtro_tipos, conn)

    with col2:
        card_alumnos_inf(cant_alumnos_inf)

    # Grafico de barras con informes de alumnos

    df_alumno_inf = q_alumno_inf(filtro_tipos, os_condition, conn)

    # Crear el gráfico
    fig_alum_inf = px.bar(
        df_alumno_inf,
        x='categoria',
        y='cantidad_alumnos',
        title='Cantidad de informes',
        labels={'categoria': 'Categoría',
                'cantidad_alumnos': 'Cantidad de alumnos'},
        text='cantidad_alumnos'
    )

    # Ajustes del gráfico
    fig_alum_inf.update_xaxes(tickangle=-45)
    fig_alum_inf.update_layout(title_x=0.5)

    with col1:
        st.plotly_chart(fig_alum_inf, use_container_width=False)