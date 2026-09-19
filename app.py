import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Generador Archivos POE", layout="centered")

st.title("Generador de Archivos para POE")
st.write("Agrega tus ecuaciones e incógnitas. La aplicación generará automáticamente el archivo de texto con el formato correcto.")

# 1. Inicializar el estado de la sesión para guardar datos temporalmente
if 'ecuaciones' not in st.session_state:
    st.session_state.ecuaciones = []
if 'variables_actuales' not in st.session_state:
    st.session_state.variables_actuales = []

st.write("---")
st.subheader("1. Armar Ecuación")

# Input para el nombre de la ecuación (Ej: Ec1)
nombre_eq = st.text_input("Nombre de la ecuación (Ej: Ec1, f1):", key="nombre_eq")

st.write("**Agregar incógnitas a esta ecuación:**")

col1, col2 = st.columns(2)
with col1:
    # Desplegable para el peso con descripciones claras
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
    # Input para la incógnita (Ej: F7, x2t)
    nombre_var = st.text_input("Variable/Incógnita (Ej: F7):", key="nombre_var")

# Botón para ir agregando variables a la ecuación actual
if st.button("➕ Agregar Variable"):
    if nombre_var.strip():
        st.session_state.variables_actuales.append({"peso": peso, "nombre": nombre_var.strip()})
        st.success(f"Variable '{nombre_var}' agregada temporalmente.")
        st.rerun()
    else:
        st.warning("Debes ingresar un nombre para la variable.")

# Mostrar las variables que se van agregando a la ecuación actual
if st.session_state.variables_actuales:
    st.info("**Variables listas para guardar en esta ecuación:**")
    for v in st.session_state.variables_actuales:
        st.write(f"- Peso: {v['peso']} | Variable: {v['nombre']}")

st.write("")
# Botón para confirmar y guardar la ecuación completa en el sistema
if st.button("💾 Guardar Ecuación Completa"):
    if nombre_eq.strip() and st.session_state.variables_actuales:
        # Guardar en la lista principal
        st.session_state.ecuaciones.append({
            "nombre": nombre_eq.strip(),
            "variables": st.session_state.variables_actuales.copy()
        })
        # Limpiar las variables actuales para empezar la siguiente ecuación
        st.session_state.variables_actuales = []
        st.success(f"Ecuación '{nombre_eq}' guardada en el sistema.")
        st.rerun()
    else:
        st.error("Falta el nombre de la ecuación o no has agregado ninguna variable.")

st.write("---")
st.subheader("2. Sistema Generado y Descarga")

# Lógica para formatear el texto exactamente como pide el POE
texto_final = ""
for ec in st.session_state.ecuaciones:
    texto_final += f"{ec['nombre']}\n"
    for var in ec['variables']:
        texto_final += f"{var['peso']} {var['nombre']}\n"
    texto_final += "\n"  # Renglón en blanco obligatorio entre ecuaciones

# Mostrar vista previa y botón de descarga si hay datos
if texto_final:
    st.text_area("Vista previa del archivo (Formato POE):", value=texto_final, height=250, disabled=True)
    
    st.download_button(
        label="⬇️ Descargar archivo .txt",
        data=texto_final,
        file_name="sistema_poe.txt",
        mime="text/plain"
    )

    if st.button("🗑️ Borrar todo e iniciar nuevo sistema"):
        st.session_state.ecuaciones = []
        st.session_state.variables_actuales = []
        st.rerun()
