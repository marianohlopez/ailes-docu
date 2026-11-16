import streamlit as st
from data.queries import q_prest_alum
from data.queries import q_alum_aut

# Cant de alumnos y cant de prestaciones

def cant_alum_prest(year_condition, tipos_seleccionados, os_condition, conn):
  
  if tipos_seleccionados:
        filtro_tipos = "AND p.prestipo_nombre_corto IN ({})".format(
                ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
            )
  else:
      filtro_tipos = "AND p.prestipo_nombre_corto IN ('')"

  cant_alumnos, cant_prestaciones, cant_admisiones, cant_activas = q_prest_alum(year_condition, 
                                                 os_condition, filtro_tipos, conn)

  card_alum = f"""
    <div class="card-container">
        <div class="card">
            <div class="card-title">Cantidad de Alumnos</div>
            <div class="card-value">{cant_alumnos}</div>
        </div>
    </div>
    """

  card_prest = f"""
    <div class="card-container">
        <div class="card">
            <div class="card-title">Cantidad de Prestaciones</div>
            <div class="card-value">{cant_prestaciones}</div>
        </div>
    </div>
    """

  card_prest_adm = f"""
    <div class="card-container">
        <div class="card">
            <div class="card-title">Cantidad de Admisiones</div>
            <div class="card-value">{cant_admisiones}</div>
        </div>
    </div>
    """

  card_prest_act = f"""
    <div class="card-container">
        <div class="card">
            <div class="card-title">Cantidad de Activas</div>
            <div class="card-value">{cant_activas}</div>
        </div>
    </div>
    """
  
  col1, col2, col3, col4 = st.columns(4)

  with col1:
      st.markdown(card_alum, unsafe_allow_html=True)

  with col2:
      st.markdown(card_prest, unsafe_allow_html=True)

  with col3:
      st.markdown(card_prest_adm, unsafe_allow_html=True)

  with col4:
      st.markdown(card_prest_act, unsafe_allow_html=True)

def porc_alum_dic(year_condition, tipos_seleccionados, os_condition, conn):

  if tipos_seleccionados:
      filtro_tipos = "AND p.prestipo_nombre_corto IN ({})".format(
              ",".join(f"'{tipo}'" for tipo in tipos_seleccionados)
          )
  else:
      filtro_tipos = "AND p.prestipo_nombre_corto IN ('')"

  porc_alumnos_dic = q_alum_aut(year_condition, os_condition, filtro_tipos, conn)

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
