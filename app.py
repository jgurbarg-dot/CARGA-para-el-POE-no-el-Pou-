import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Generador Archivos POE", layout="centered")

# 1. Inicializar el estado de la sesión para guardar datos
if 'ecuaciones' not in st.session_state:
    st.session_state.ecuaciones = []
if 'variables_actuales' not in st.session_state:
    st.session_state.variables_actuales = []

st.title("Generador de Archivos para POE")
st.write("Agrega tus ecuaciones e incógnitas. Las variables repetidas en distintas ecuaciones se guardarán correctamente.")
st.write("---")

st.subheader("1. Armar Ecuación")

# Input para el nombre de la ecuación. Al estar fuera del form, no se borra.
nombre_eq = st.text_input("Nombre de la ecuación (Ej: E1, E2):", key="nombre_eq")

st.write("**Agregar incógnitas a esta ecuación:**")

# Usamos st.form para que al agregar una variable, la caja de texto se limpie automáticamente
with st.form("formulario_variables", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        opciones_peso = {
            1: "1 (Fácil de despejar)", 2: "2", 3: "3", 4: "4", 5: "5",
            6: "6", 7: "7", 8: "8", 9: "9", 10: "10 (Muy complicado)"
        }
        peso = st.selectbox(
            "Peso de la incógnita:", 
            options=list(opciones_peso.keys()), 
            format_func=lambda x: opciones_peso[x]
        )
    with col2:
        nombre_var = st.text_input("Variable/Incógnita (Ej: F3, F2):")

    # Botón de envío del formulario
    btn_agregar = st.form_submit_button("➕ Agregar Variable")
    
    if btn_agregar:
        if nombre_var.strip():
            # Guarda la variable sin importar si ya existe (permite repeticiones)
            st.session_state.variables_actuales.append({"peso": peso, "nombre": nombre_var.strip()})
            st.success(f"Variable '{nombre_var.strip()}' agregada a la lista temporal.")
            st.rerun() # Fuerza a recargar para mostrar la variable abajo inmediatamente
        else:
            st.warning("Debes ingresar un nombre para la variable.")

# Mostrar las variables que se van agregando a la ecuación actual y permitir borrarlas
if st.session_state.variables_actuales:
    st.info("**Variables listas para guardar en la ecuación:**")
    for i, v in enumerate(st.session_state.variables_actuales):
        colA, colB = st.columns([0.85, 0.15])
        colA.write(f"- Peso: {v['peso']} | Variable: **{v['nombre']}**")
        # Botón para borrar esta variable específica
        if colB.button("❌ Borrar", key=f"del_var_{i}", help="Eliminar esta variable de la ecuación actual"):
            st.session_state.variables_actuales.pop(i)
            st.rerun()

st.write("")
# Botón para confirmar y guardar la ecuación completa en el sistema
if st.button("💾 Guardar Ecuación Completa"):
    if nombre_eq.strip() and st.session_state.variables_actuales:
        # Guardar en la lista principal
        st.session_state.ecuaciones.append({
            "nombre": nombre_eq.strip(),
            "variables": st.session_state.variables_actuales.copy()
        })
        # Limpiar SOLO las variables actuales para empezar la siguiente ecuación
        st.session_state.variables_actuales = []
        st.success(f"Ecuación '{nombre_eq.strip()}' guardada en el sistema. Puedes cambiar el nombre arriba y seguir agregando.")
        st.rerun()
    else:
        st.error("Falta el nombre de la ecuación o no has agregado ninguna variable a la lista.")

st.write("---")
st.subheader("2. Sistema Generado y Descarga")

# Mostrar las ecuaciones guardadas y permitir borrarlas individualmente
if st.session_state.ecuaciones:
    st.write("**Ecuaciones confirmadas en el sistema:**")
    for i, ec in enumerate(st.session_state.ecuaciones):
        col_eq1, col_eq2 = st.columns([0.85, 0.15])
        # Muestra el nombre de la ec y un resumen de sus variables
        nombres_vars = ", ".join([v['nombre'] for v in ec['variables']])
        col_eq1.write(f"**{ec['nombre']}** *(Variables: {nombres_vars})*")
        
        # Botón para borrar toda la ecuación
        if col_eq2.button("❌ Borrar", key=f"del_eq_{i}", help="Eliminar esta ecuación completa del sistema"):
            st.session_state.ecuaciones.pop(i)
            st.rerun()

st.write("")

# Lógica para formatear el texto exactamente como pide el POE (Estilo Windows)
texto_final = ""
for i, ec in enumerate(st.session_state.ecuaciones):
    texto_final += f"{ec['nombre']}\r\n"
    for var in ec['variables']:
        texto_final += f"{var['peso']} {var['nombre']}\r\n"
    
    # Agrega el renglón en blanco SOLO si no es la última ecuación de la lista
    if i < len(st.session_state.ecuaciones) - 1:
        texto_final += "\r\n"

# Mostrar vista previa y botón de descarga si hay datos
if texto_final:
    st.text_area("Vista previa del archivo (Formato POE):", value=texto_final, height=350, disabled=True)
    
    st.download_button(
        label="⬇️ Descargar archivo .txt",
        data=texto_final,
        file_name="sistema_poe.txt",
        mime="text/plain"
    )

    if st.button("🗑️ Borrar TODO e iniciar nuevo sistema"):
        st.session_state.ecuaciones = []
        st.session_state.variables_actuales = []
        st.rerun()
