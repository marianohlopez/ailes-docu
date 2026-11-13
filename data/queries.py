import pandas as pd
from sqlalchemy import text

def q_filter_os(conn):
  q_os = """ 
      SELECT 
        o.os_nombre
      FROM v_os o 
      JOIN v_prestaciones p
        ON o.os_id = p.prestacion_os
      WHERE 
        p.prestacion_estado = 1
        AND p.prestacion_id >= 1
        AND p.prestacion_alumno != 522
  """

  return pd.read_sql(q_os, conn)

# Tarjetas - cant de alumnos y cant de prestaciones

def q_prest_alum(year_condition, c1, c2, conn):
    q_prest_alum = f"""
    SELECT 
        COUNT(DISTINCT a.alumno_id) AS cant_alumnos,
        COUNT(DISTINCT p.prestacion_id) AS cant_prestaciones
    FROM v_os o 
    JOIN v_prestaciones p 
        ON p.prestacion_os = o.os_id
    JOIN v_alumnos a 
        ON p.alumno_id = a.alumno_id
    WHERE 
        p.prestacion_estado = 1
        {year_condition}
        AND p.prestacion_id NOT IN (521,1950)
        AND p.prestacion_alumno != 522
    {c1}
    {c2}
    """
    df_prest_alum = pd.read_sql(q_prest_alum, conn)

    # Extraer los valores
    cant_alumnos = df_prest_alum['cant_alumnos'][0]
    cant_prestaciones = df_prest_alum['cant_prestaciones'][0]

    return cant_alumnos, cant_prestaciones


# Tarjeta - Porcentaje de alumnos autorizados hasta diciembre
def q_alum_aut(year_condition, os_condition, filtro_tipos, conn): 

  q_alum_aut = f"""
    SELECT 
        ROUND(
            (SUM(CASE WHEN MONTH(p.prestacion_fec_aut_OS_hasta) = 12 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
        ) AS porcentaje_diciembre
    FROM v_prestaciones p 
    JOIN v_os o 
        ON p.prestacion_os = o.os_id
    WHERE 
        prestacion_estado = 1
        {year_condition}
        AND prestacion_fec_aut_OS_hasta IS NOT NULL
        AND p.prestacion_alumno != 522
        {filtro_tipos}
        {os_condition};
"""

  df_alum_aut = pd.read_sql(q_alum_aut, conn)

  # Extraer los valores
  return df_alum_aut['porcentaje_diciembre'][0]

# Grafico de barras-cant de prestaciones por obra social

def q_alum_os(year_condition, os_condition, filtro_tipos, conn):
  q_alum_os = f"""
      SELECT 
        o.os_nombre AS obra_social, COUNT(p.prestacion_id) AS cantidad_prestaciones
      FROM v_prestaciones p 
      JOIN v_os o 
        ON p.prestacion_os = o.os_id
      WHERE 
        prestacion_estado = 1
        {year_condition}
        AND p.prestacion_alumno != 522
        {filtro_tipos}
        {os_condition}
      GROUP BY obra_social;
  """
  df_alum_os = pd.read_sql(q_alum_os, conn)

  # Asegurar orden correcto
  return df_alum_os.sort_values('cantidad_prestaciones', ascending=False)

# Grafico de linea histórico de activaciones

def q_fec_aut(filtro_tipos, os_condition, conn):
   
    q_altas_bajas = f"""
        SELECT 
            periodo,
            SUM(cant_altas) AS cant_altas,
            SUM(cant_bajas) AS cant_bajas
        FROM (
            SELECT 
                DATE_FORMAT(prestacion_fec_pase_activo, '%%Y-%%m') AS periodo,
                COUNT(*) AS cant_altas,
                0 AS cant_bajas
            FROM v_prestaciones p
			JOIN v_os o 
                ON p.prestacion_os = o.os_id
            WHERE prestacion_fec_pase_activo IS NOT NULL
                AND p.prestacion_anio IN (2026, 2027)
                AND p.prestacion_alumno != 522
            {filtro_tipos}
            {os_condition}
            GROUP BY DATE_FORMAT(prestacion_fec_pase_activo, '%%Y-%%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(prestacion_fec_baja, '%%Y-%%m') AS periodo,
                0 AS cant_altas,
                COUNT(*) AS cant_bajas
            FROM v_prestaciones p
			JOIN v_os o 
                ON p.prestacion_os = o.os_id
            WHERE prestacion_fec_baja IS NOT NULL
                AND prestacion_fec_pase_activo IS NOT NULL
                AND p.prestacion_anio IN (2026, 2027)
                AND p.prestacion_alumno != 522
            {filtro_tipos}
            {os_condition}
            GROUP BY DATE_FORMAT(prestacion_fec_baja, '%%Y-%%m')
        ) t
        GROUP BY periodo
        ORDER BY periodo;
    """
   
    df_altas_bajas = pd.read_sql(q_altas_bajas, conn)

    return df_altas_bajas

def os_filter(os):
  if os is None:
    return "", {}

  placeholders = ", ".join(
    [f":os_{i}" for i in range(len(os))]
  )

  params = {
    f"os_{i}": valor
    for i, valor in enumerate(os)
  }

  return f"AND o.os_nombre IN ({placeholders})", params

SUBQUERY_TERAPIAS = """
  SELECT DISTINCT prestacion_alumno
  FROM v_prestaciones
  WHERE prestacion_anio IN (2026, 2027)
    AND prestipo_nombre_corto = 'TERAPIAS'
    AND prestacion_estado IN (0,1)
"""

def terapy_filter(mode=None):
  if mode is None:
    return ""

  if mode == "exclude":
    return f"AND p.prestacion_alumno NOT IN ({SUBQUERY_TERAPIAS})"

  raise ValueError("mode debe ser None o 'exclude'")

def extract_indic(conn, os=None, terapias=None):
  os_clause, params = os_filter(os)
  terapy_clause = terapy_filter(terapias)
  query = f""" 
    SELECT 
      CONCAT(p.alumno_apellido, ', ', p.alumno_nombre) AS nombre_alumno,
      p.prestacion_id,
      p.prestacion_anio, 
      p.prestacion_estado,
      p.prestacion_renueva_prox,
      p.prestipo_nombre_corto,
      o.os_nombre,
      MAX(p.prestacion_fec1) AS revision,
      MAX(p.prestacion_fec2) AS armado,
      MAX(p.prestacion_fec3) AS envio_retiro
    FROM v_prestaciones p 
    LEFT JOIN v_os o
      ON p.prestacion_os = o.os_id
    WHERE
      p.prestacion_estado IN (0,1)
      AND p.prestacion_anio IN (2026, 2027)
      AND p.prestacion_alumno NOT IN (522, 1372, 572)
      {terapy_clause}
      {os_clause}
    GROUP BY p.prestacion_id
    ORDER BY nombre_alumno;
  """

  with conn.connect() as connection:
    result = connection.execute(text(query), params)
    rows = result.fetchall()

  return rows

def extract_indic_terapias(conn):
  query = f"""
    SELECT
      CONCAT(p.alumno_apellido, ', ', p.alumno_nombre) AS nombre_alumno,
      p.prestacion_id,
      p.prestacion_anio, 
      p.prestacion_estado,
      p.prestacion_renueva_prox,
      p.prestipo_nombre_corto,
      o.os_nombre,
      MAX(p.prestacion_fec1) AS revision,
      MAX(p.prestacion_fec2) AS armado,
      MAX(p.prestacion_fec3) AS envio_retiro
    FROM v_prestaciones p
    LEFT JOIN v_os o 
      ON p.prestacion_os = o.os_id
    WHERE
      p.prestacion_estado IN (0,1)
      AND p.prestacion_anio IN (2026, 2027)
      AND p.prestacion_alumno NOT IN (522, 1372, 572)
      AND p.prestacion_alumno IN ({SUBQUERY_TERAPIAS})
    GROUP BY p.prestacion_id
    ORDER BY nombre_alumno
  """
  with conn.connect() as connection:
        result = connection.execute(text(query))
        rows = result.fetchall()

  return rows
