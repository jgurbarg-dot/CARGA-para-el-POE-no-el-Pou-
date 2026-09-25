import streamlit as st
import re

# Configuración de la página
st.set_page_config(page_title="Generador Archivos POE", layout="centered")

# 1. Inicializar el estado de la sesión
if 'ecuaciones' not in st.session_state:
    st.session_state.ecuaciones = []
if 'variables_actuales' not in st.session_state:
    st.session_state.variables_actuales = []

# Diccionario global de pesos
opciones_peso = {
    1: "1 (Fácil de despejar)", 2: "2", 3: "3", 4: "4", 5: "5",
    6: "6", 7: "7", 8: "8", 9: "9", 10: "10 (Muy complicado)"
}

st.title("Generador Avanzado POE")
st.write("Procesa ecuaciones automáticamente o cárgalas de forma manual. Edita pesos y variables antes de exportar.")
st.write("---")

# ==========================================
# SECCIÓN 1: CARGA AUTOMÁTICA (NUEVO)
# ==========================================
st.subheader("🤖 1. Carga Automática (Desde Texto)")
st.info("Copia y pega tus ecuaciones y tus datos. El sistema cruzará la información y extraerá solo las incógnitas con peso 1 por defecto.")

col_text1, col_text2 = st.columns(2)
with col_text1:
    texto_eqs = st.text_area("Pega tus ecuaciones (Ej: F10 * xb10 + F9 * xb9 = F11 * xb11 E2):", height=200)
with col_text2:
    texto_datos = st.text_area("Pega tus datos/constantes (Ej: F4=100, xd11=0.01, aa=0.5):", height=200)

if st.button("⚡ Procesar Texto Automáticamente"):
    if texto_eqs.strip():
        # Extraer nombres de variables de los datos conocidos (letras seguidas de letras/números)
        datos_conocidos = set(re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b', texto_datos))
        
        lineas = texto_eqs.split('\n')
        agregadas = 0
        
        for linea in lineas:
            linea = linea.strip()
            if not linea: continue
            
            # Buscar el nombre de la ecuación (Ej: E1, E12)
            match_nombre = re.search(r'\bE\d+\b', linea)
            nombre_eq = match_nombre.group() if match_nombre else f"Eq_{len(st.session_state.ecuaciones)+1}"
            
            # Limpiar la E de la ecuación para no contarla como variable
            linea_limpia = re.sub(r'\bE\d+\b', '', linea)
            
            # Encontrar todas las variables puras en la ecuación
            vars_en_linea = set(re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b', linea_limpia))
            
            # CRUZAR: Restar los datos fijos para dejar solo las incógnitas reales
            incognitas = vars_en_linea - datos_conocidos
            
            # CHECK DE INDEPENDENCIA BÁSICA: Si no hay incógnitas, la descarta.
            if not incognitas:
                st.warning(f"⚠️ Ecuación ignorada: **{nombre_eq}**. No posee incógnitas libres (está completamente definida por los datos fijos).")
                continue
            
            # Guardar la ecuación con las incógnitas resultantes a peso 1
            vars_a_guardar = [{"nombre": v, "peso": 1} for v in incognitas]
            st.session_state.ecuaciones.append({
                "nombre": nombre_eq,
                "variables": vars_a_guardar
            })
            agregadas += 1
            
        if agregadas > 0:
            st.success(f"✅ Se procesaron e integraron {agregadas} ecuaciones al sistema.")
    else:
        st.error("Debes ingresar ecuaciones para procesar.")

st.write("---")

# ==========================================
# SECCIÓN 2: CARGA MANUAL (EXISTENTE)
# ==========================================
st.subheader("✍️ 2. Carga Manual")

nombre_eq_manual = st.text_input("Nombre de la ecuación (Ej: E1):", key="nombre_eq")

with st.form("formulario_variables", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        peso = st.selectbox("Peso de la incógnita:", options=list(opciones_peso.keys()), format_func=lambda x: opciones_peso[x])
    with col2:
        nombre_var = st.text_input("Variable/Incógnita (Ej: F3):")

    btn_agregar = st.form_submit_button("➕ Agregar Variable")
    
    if btn_agregar:
        if nombre_var.strip():
            st.session_state.variables_actuales.append({"peso": peso, "nombre": nombre_var.strip()})
            st.success(f"Variable '{nombre_var.strip()}' en lista temporal.")
            st.rerun()
        else:
            st.warning("Debes ingresar un nombre.")

if st.session_state.variables_actuales:
    st.info("**Variables temporales:**")
    for i, v in enumerate(st.session_state.variables_actuales):
        colA, colB = st.columns([0.85, 0.15])
        colA.write(f"- Peso: {v['peso']} | Variable: **{v['nombre']}**")
        if colB.button("❌", key=f"del_tmp_{i}"):
            st.session_state.variables_actuales.pop(i)
            st.rerun()

if st.button("💾 Guardar Ecuación Manual"):
    if nombre_eq_manual.strip() and st.session_state.variables_actuales:
        st.session_state.ecuaciones.append({
            "nombre": nombre_eq_manual.strip(),
            "variables": st.session_state.variables_actuales.copy()
        })
        st.session_state.variables_actuales = []
        st.rerun()
    else:
        st.error("Falta nombre o variables.")

st.write("---")

# ==========================================
# SECCIÓN 3: EDICIÓN DINÁMICA Y DESCARGA
# ==========================================
st.subheader("⚙️ 3. Sistema Generado y Edición")

if st.session_state.ecuaciones:
    st.write("**Panel de Control:** Aquí puedes cambiar el peso de cualquier variable o eliminar elementos.")
    
    # Mostrar cada ecuación en un desplegable para mantenerlo ordenado
    for i, ec in enumerate(st.session_state.ecuaciones):
        with st.expander(f"📦 {ec['nombre']} (Ver/Editar Variables)"):
            # Botón para borrar toda la ecuación
            if st.button(f"🗑️ Eliminar Ecuación Completa {ec['nombre']}", key=f"del_eq_{i}"):
                st.session_state.ecuaciones.pop(i)
                st.rerun()
            
            st.write("---")
            # Iterar sobre las variables de esa ecuación
            for j, var in enumerate(ec['variables']):
                col_var_name, col_var_peso, col_var_del = st.columns([0.4, 0.4, 0.2])
                
                col_var_name.write(f"**{var['nombre']}**")
                
                # Desplegable para editar el peso dinámicamente
                nuevo_peso = col_var_peso.selectbox(
                    "Peso:", 
                    options=list(opciones_peso.keys()), 
                    format_func=lambda x: opciones_peso[x],
                    index=list(opciones_peso.keys()).index(var['peso']),
                    key=f"edit_peso_{i}_{j}"
                )
                
                # Actualizar el peso en la base de datos de la sesión
                if nuevo_peso != var['peso']:
                    st.session_state.ecuaciones[i]['variables'][j]['peso'] = nuevo_peso
                
                # Botón para borrar la variable de esta ecuación particular
                if col_var_del.button("❌ Quitar", key=f"del_var_{i}_{j}"):
                    st.session_state.ecuaciones[i]['variables'].pop(j)
                    st.rerun()

st.write("")

# Lógica para formatear el texto a POE
texto_final = ""
for i, ec in enumerate(st.session_state.ecuaciones):
    # Si la ecuación se quedó vacía porque le borraste todas las variables, se ignora
    if not ec['variables']: continue
    
    texto_final += f"{ec['nombre']}\r\n"
    for var in ec['variables']:
        texto_final += f"{var['peso']} {var['nombre']}\r\n"
    
    if i < len(st.session_state.ecuaciones) - 1:
        texto_final += "\r\n"

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
