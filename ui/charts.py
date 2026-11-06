import streamlit as st
import plotly.express as px
from data.queries import q_alum_os
from data.queries import q_fec_aut


#--- Grafico de barras-cant de prestaciones por obra social

def chart_prest_os(year_condition, tipos_seleccionados, os_condition, conn):
  
  if tipos_seleccionados:
      filtro_tipos = "AND p.prestipo_nombre_corto IN ({})".format(
              ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
          )
  else:
      filtro_tipos = "AND p.prestipo_nombre_corto IN ('')"

  df_alum_os = q_alum_os(year_condition, os_condition, filtro_tipos, conn)

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
  

    df = q_fec_aut(filtro_tipos, os_condition, conn)

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


