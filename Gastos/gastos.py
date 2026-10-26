

import sqlite3
from pathlib import Path
from datetime import date
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Mis Gastos",
    page_icon="💰"
)

# Ruta del archivo en donde se guardan los gastos
rutadb = Path(__file__).parent / "datos.db"

# Conectar con SQLite
conexion = sqlite3.connect(rutadb)

# Creamos el sqlite ( tabla si todavia no hay)
conexion.execute("""
    CREATE TABLE IF NOT EXISTS datos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concepto TEXT NOT NULL,
        cantidad REAL NOT NULL,
        fecha TEXT NOT NULL
    )
""")
conexion.commit()

# Streamlit
st.title("Mis gastos")
st.write("Registra y consulta tus gastos")

# formulario
with st.form("formulario_gasto"):

    # text_input texto en vez de input
    concepto = st.text_input("¿Concepto del Gasto?")

    # number_input para numeros
    cantidad = st.number_input(
        "Cantidad del gasto ($)",
        min_value=0.01,
        value=50.0,
        step=5.0
    )

    # date fecha
    fecha_gasto = st.date_input(
        "Fecha del gasto",
        value=date.today()
    )

    # enviar datos
    guardar = st.form_submit_button("Guardar gasto")

# Guardar 
if guardar:

    # Comprobar no vacio
    if concepto.strip():

        # Insertar el gasto
        conexion.execute("""
            INSERT INTO datos (concepto, cantidad, fecha)
            VALUES (?, ?, ?)
        """, (
            concepto.strip(),
            cantidad,
            fecha_gasto.isoformat()
        ))

        conexion.commit()
        st.success("¡Gasto guardado correctamente!")

    else:
        st.error("Escribe el concepto del gasto.")

# Gastos
st.subheader("Historial")

# Obtener todos los registros
datos = conexion.execute("""
    SELECT id, concepto, cantidad, fecha
    FROM datos
    ORDER BY fecha DESC, id DESC
""").fetchall()

# Mostrar los gastos como una tabla
if datos:
    st.dataframe(
        [
            {
                "ID": fila[0],
                "Concepto": fila[1],
                "Cantidad ($)": fila[2],
                "Fecha": fila[3]
            }
            for fila in datos
        ],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No hay informacion todavia...")

# CALCULAR EL TOTAL ACUMULADO
total = conexion.execute("""
    SELECT SUM(cantidad) FROM datos
""").fetchone()[0]

# st.metric muestra un indicador destacado
st.metric("Total gastado...", f"${total or 0:,.2f}")

# Cerrar la conexión con SQLite
conexion.close()
