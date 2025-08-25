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

def chart_fec_aut(tipos_seleccionados, os_condition, conn):
  
    if tipos_seleccionados:
        filtro_tipos = "AND p.prestipo_nombre_corto IN ({})".format(
                ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
            )
    else:
        filtro_tipos = "AND p.prestipo_nombre_corto IN ('')"
  

    df_fec_aut = q_fec_aut(filtro_tipos, os_condition, conn)

    # Conteo de prestaciones por mes
    serie = (
        df_fec_aut.groupby("year_month", as_index=False)
            .size()                         
            .rename(columns={"size": "prestaciones"})
            .sort_values("year_month")
    )

    today = pd.Timestamp(datetime.today().replace(day=1))
    max_fecha = max(serie["year_month"].max(), today)

    full_range = pd.date_range(
        serie["year_month"].min(), max_fecha, freq="MS"
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

# Grafico Fechas de finalizacion de autorizaciones

def chart_fin_aut(os_condition):   

  df_fec_aut = q_fin_aut(os_condition)

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