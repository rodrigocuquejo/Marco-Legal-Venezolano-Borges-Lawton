import streamlit as st
import sqlite3
import os

# Configuración de la página
st.set_page_config(
    page_title="Borges & Lawton | Inteligencia Legal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de Colores Corporativa (Estilo Lujo / Legal)
COLOR_FONDO_MARFIL = "#F9F8F3"      
COLOR_AZUL_OXFORD = "#1A2E40"       
COLOR_DORADO_MUTED = "#C5A059"      
COLOR_NOGAL = "#3D3A35"             

# Inyección de estilos CSS avanzados
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_MARFIL}; }}
    
    .brand-title {{ font-family: 'Times New Roman', Times, serif; color: {COLOR_AZUL_OXFORD}; font-size: 34px; font-weight: bold; letter-spacing: 2px; }}
    .brand-subtitle {{ font-family: 'Arial', sans-serif; color: {COLOR_DORADO_MUTED}; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; margin-top: -5px; margin-bottom: 30px; }}
    
    .main-header {{ text-align: center; color: {COLOR_AZUL_OXFORD}; font-family: 'Times New Roman', serif; font-size: 28px; font-weight: bold; margin: 40px 0 5px 0; }}
    .main-subheader {{ text-align: center; color: #64748B; font-size: 14px; margin-bottom: 45px; font-family: 'Georgia', serif; font-style: italic; }}
    
    div.stButton > button {{
        background-color: #FFFFFF !important;
        color: {COLOR_AZUL_OXFORD} !important;
        border: 1px solid #E2E8F0 !important;
        border-bottom: 4px solid {COLOR_DORADO_MUTED} !important;
        border-radius: 4px !important;
        height: 120px !important;
        box-shadow: 0 4px 12px rgba(42, 27, 18, 0.02) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div.stButton > button:hover {{
        border-color: {COLOR_AZUL_OXFORD} !important;
        box-shadow: 0 6px 16px rgba(26, 46, 64, 0.08) !important;
        transform: translateY(-2px);
    }}
    div.stButton > button p {{
        font-size: 16px !important;
        font-weight: bold !important;
        font-family: 'Times New Roman', Times, serif !important;
        color: {COLOR_NOGAL} !important;
        white-space: normal !important;
        line-height: 1.3 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Encabezado de la firma
st.markdown('<div class="brand-title">BORGES & LAWTON</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Inteligencia Legal • Repositorio Corporativo</div>', unsafe_allow_html=True)
st.markdown('<hr style="border: 0; height: 1px; background: #E2E8F0; margin-bottom: 40px;">', unsafe_allow_html=True)

# Título central de la herramienta
st.markdown('<div class="main-header">Marco Legal Venezolano</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subheader">Seleccione un área del derecho o realice una búsqueda específica</div>', unsafe_allow_html=True)

# Mapeo de categorías con sus íconos
CATEGORIAS = {
    "Civil, Mercantil y Registral": "📜",
    "Constitucional": "🏛️",
    "Laboral y Seguridad Social": "💼",
    "Menores y Mujeres": "👥",
    "Penal": "⚖️",
    "Petróleo": "🛢️",
    "Químicos, Minas, Energía": "⚡",
    "Tributario y Financiero": "💰"
}

DB_NAME = "borges_lawton_legal.db"

# Función para obtener leyes por categoría
def obtener_leyes_por_categoria(categoria_nombre):
    if not os.path.exists(DB_NAME):
        return []
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, subcategoria, enlace_pdf FROM leyes WHERE categoria = ?", (categoria_nombre,))
        leyes = cursor.fetchall()
        conn.close()
        return leyes
    except Exception:
        return []

# Función para la búsqueda específica de palabras clave o artículos
def obtener_busqueda_especifica(texto_buscar):
    if not os.path.exists(DB_NAME):
        return []
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Busca coincidencia en el nombre o texto de la ley
        query = "SELECT id, nombre, categoria, enlace_pdf FROM leyes WHERE nombre LIKE ? OR categoria LIKE ?"
        cursor.execute(query, (f"%{texto_buscar}%", f"%{texto_buscar}%"))
        resultados = cursor.fetchall()
        conn.close()
        return resultados
    except Exception:
        return []

# --- INICIALIZACIÓN DE MEMORIA DE SESIÓN ---
if 'categoria_seleccionada' not in st.session_state:
    st.session_state.categoria_seleccionada = None
if 'indice_resultado' not in st.session_state:
    st.session_state.indice_resultado = 0

# Grid de categorías (Botones principales)
keys = list(CATEGORIAS.keys())
rows = [keys[0:4], keys[4:8]]

for row in rows:
    cols = st.columns(4)
    for i, cat in enumerate(row):
        with cols[i]:
            texto_boton = f"{CATEGORIAS[cat]}\n\n{cat}"
            if st.button(texto_boton, key=f"btn_{cat}", use_container_width=True):
                st.session_state.categoria_seleccionada = cat
                st.session_state.busqueda_activa = False # Desactiva búsqueda si se filtra por botón

st.markdown("<br><br>", unsafe_allow_html=True)

# --- SECCIÓN DE BÚSQUEDA ESPECÍFICA CON MEMORIA ---
st.markdown("### 🔍 Buscador Avanzado Especializado")
busqueda = st.text_input("Escriba el artículo, palabra clave o ley que desea localizar:")

if busqueda:
    st.session_state.categoria_seleccionada = None # Limpia el filtro de botones si el usuario escribe
    resultados = obtener_busqueda_especifica(busqueda)
    
    if resultados:
        total_resultados = len(resultados)
        
        # Validar límites del índice
        if st.session_state.indice_resultado >= total_resultados:
            st.session_state.indice_resultado = 0
            
        resultado_actual = resultados[st.session_state.indice_resultado]
        
        # Cuadro elegante para el resultado
        st.info(f"Coincidencia {st.session_state.indice_resultado + 1} de {total_resultados} encontradas.")
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"<p style='font-size:20px; font-family:\"Times New Roman\", serif; color:{COLOR_AZUL_OXFORD};'><b>{resultado_actual[1]}</b></p>", unsafe_allow_html=True)
            st.caption(f"Categoría: {resultado_actual[2]}")
        with col_btn:
            if resultado_actual[3]: # Si tiene enlace PDF
                st.markdown(f'<a href="{resultado_actual[3]}" target="_blank"><button style="width:100%; height:45px; background-color:{COLOR_AZUL_OXFORD}; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">📄 Ver Documento PDF</button></a>', unsafe_allow_html=True)
            else:
                st.button("PDF no disponible", key=f"no_pdf_{resultado_actual[0]}", disabled=True)
        
        # Botones de navegación (Salto de resultados)
        st.markdown("<br>", unsafe_allow_html=True)
        col_ant, col_sig = st.columns(2)
        with col_ant:
            if st.button("⬅️ Resultado Anterior", use_container_width=True):
                if st.session_state.indice_resultado > 0:
                    st.session_state.indice_resultado -= 1
                    st.rerun()
        with col_sig:
            if st.button("Siguiente Resultado ➡️", use_container_width=True):
                if st.session_state.indice_resultado < total_resultados - 1:
                    st.session_state.indice_resultado += 1
                    st.rerun()
    else:
        st.warning("No se encontraron coincidencias exactas para su búsqueda.")
else:
    st.session_state.indice_resultado = 0

# --- SECCIÓN DE BOTONES DE CATEGORÍAS (RESULTADOS) ---
if st.session_state.categoria_seleccionada:
    cat_sel = st.session_state.categoria_seleccionada
    st.markdown("---")
    st.markdown(f"### {CATEGORIAS[cat_sel]} Documentos en: {cat_sel}")
    
    leyes_encontradas = obtener_leyes_por_categoria(cat_sel)
    
    if leyes_encontradas:
        for id_ley, nombre_ley, subcat, enlace in leyes_encontradas:
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:10px 5px; font-weight:bold; color:#64748B; font-size:12px; border-bottom:2px solid #E2E8F0;">
                    <span>📌 {subcat.upper() if subcat else 'GENERAL'}</span>
                </div>
            """, unsafe_allow_html=True)
            
            col_info_cat, col_btn_cat = st.columns([4, 1])
            with col_info_cat:
                st.markdown(f"<p style='font-size:18px; font-family:\"Times New Roman\", serif; color:{COLOR_AZUL_OXFORD}; margin-top:10px;'><b>{nombre_ley}</b></p>", unsafe_allow_html=True)
            with col_btn_cat:
                if enlace:
                    st.markdown(f'<a href="{enlace}" target="_blank"><button style="width:100%; height:40px; margin-top:5px; background-color:{COLOR_AZUL_OXFORD}; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">📄 Abrir PDF</button></a>', unsafe_allow_html=True)
                else:
                    st.button("No disponible", key=f"no_dis_{id_ley}", disabled=True)
    else:
        st.info("No se encontraron leyes registradas en esta categoría dentro de la base de datos.")