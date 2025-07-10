import streamlit as st
from data.queries import q_prest_alum
from data.queries import q_alum_aut

# Cant de alumnos y cant de prestaciones

def cant_alum_prest(os_condition, conn):

  cant_alumnos, cant_prestaciones = q_prest_alum(os_condition, "", conn)

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
  col1, col2 = st.columns(2)

  with col1:
      st.markdown(card_alum, unsafe_allow_html=True)

  with col2:
      st.markdown(card_prest, unsafe_allow_html=True)

def porc_alum_dic(os_condition, conn):

  porc_alumnos_dic = q_alum_aut(os_condition, conn)

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

def card_alumnos_inf(cant_alumnos_inf):

  st.markdown(f"""
        <div class="card-container">
            <div class="card">
                <div class="card-title">Cantidad de Alumnos</div>
                <div class="card-value">{cant_alumnos_inf}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)