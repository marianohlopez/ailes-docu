import pandas as pd
from .connection import get_connection

conn = get_connection()

def q_filter_os():
  q_os = """ 
      SELECT o.os_nombre
      FROM v_os o JOIN v_prestaciones p
      ON o.os_id = p.prestacion_os
      WHERE p.prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
    AND p.prestacion_id >= 1
  """

  return pd.read_sql(q_os, conn)

# Tarjetas - cant de alumnos y cant de prestaciones

def q_prest_alum(c1, c2):
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


# Tarjeta - Porcentaje de alumnos autorizados hasta diciembre
def q_alum_aut(os_condition): 

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
  return df_alum_aut['porcentaje_diciembre'][0]

# Grafico de barras-cant de prestaciones por obra social

def q_alum_os(os_condition):

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
  return df_alum_os.sort_values('cantidad_prestaciones', ascending=False)

# Grafico de barras-cant de prestaciones por obra social

def q_alum_os(os_condition):
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
  return df_alum_os.sort_values('cantidad_prestaciones', ascending=False)

# Grafico de linea histórico de activaciones

def q_fec_aut(os_condition):

  q_fec_aut = f"""
  SELECT o.os_nombre, p.prestacion_fec_aut_os
      FROM v_prestaciones p JOIN v_os o 
      ON p.prestacion_os = o.os_id
      WHERE prestacion_estado_descrip = "ACTIVA" COLLATE utf8mb4_0900_ai_ci
      {os_condition}
  """

  df_fec_aut = pd.read_sql(q_fec_aut, conn)

  df_fec_aut["prestacion_fec_aut_OS"] = pd.to_datetime(df_fec_aut["prestacion_fec_aut_OS"])

  df_fec_aut["year_month"] = df_fec_aut["prestacion_fec_aut_OS"].dt.to_period("M").dt.to_timestamp()

  return df_fec_aut

# Grafico Fechas de finalizacion de autorizaciones

def q_fin_aut(os_condition):

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

  return pd.read_sql(q_fec_aut, conn)

def q_alumno_inf(filtro_informes,os_condition):

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
    return pd.read_sql(q_alumno_inf, conn)