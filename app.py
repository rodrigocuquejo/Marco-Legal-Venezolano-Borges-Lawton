import streamlit as st
import sqlite3
import os
import re
import unicodedata
import time

# --- CONFIGURACIÓN DE PÁGINA NATIVA ---
st.set_page_config(
    page_title="Borges & Lawton | Inteligencia Legal",
    layout="wide",
    page_icon="⚖️"
)

# PALETA DE COLORES HIGH-END EXECUTIVE
COLOR_AZUL_OXFORD = "#1B2A4A"   
COLOR_DORADO_MUTED = "#C5A059"  
COLOR_NOGAL = "#2A1B12"         
COLOR_FONDO_MARFIL = "#FDFBF7"  

# --- FUNCIÓN PARA ELIMINAR ACENTOS ---
def remover_acentos(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# --- DICCIONARIO DE ICONOS VECTORIALES SVG MINIMALISTAS ---
DICT_ICONOS = {
    "Civil, Mercantil y Registral": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
        </svg>
    </div>
    """,
    "Laboral y Seguridad Social": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
        </svg>
    </div>
    """,
    "Tributario y Financiero": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="1" x2="12" y2="23"></line>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
        </svg>
    </div>
    """,
    "Químicos, Minas y Energía": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polyline>
        </svg>
    </div>
    """,
    "Petróleo": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22a7 7 0 0 0 7-7c0-4.3-7-9-7-9s-7 4.7-7 9a7 7 0 0 0 7 7z"></path>
        </svg>
    </div>
    """,
    "Constitucional": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            <line x1="9" y1="6" x2="15" y2="6"></line>
            <line x1="9" y1="10" x2="15" y2="10"></line>
        </svg>
    </div>
    """,
    "Penal": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 5 4 4M8 12l4 4M3 21l8-8M17 3l4 4-7 7-4-4z"></path>
        </svg>
    </div>
    """,
    "Menores y Mujeres": """
    <div style="text-align: center; margin-bottom: 12px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#C5A059" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
        </svg>
    </div>
    """
}

# --- ESTILOS VISUALES CORPORATIVOS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_MARFIL}; }}
    
    .brand-title {{ font-family: 'Times New Roman', Times, serif; color: {COLOR_AZUL_OXFORD}; font-size: 34px; font-weight: bold; letter-spacing: 2px; }}
    .brand-subtitle {{ font-family: 'Arial', sans-serif; color: {COLOR_DORADO_MUTED}; font-size: 11px; letter-spacing: 4px; text-transform: uppercase; margin-top: 5px; font-weight: 600; }}
    
    .main-header {{ text-align: center; color: {COLOR_AZUL_OXFORD}; font-family: 'Times New Roman', serif; font-size: 28px; font-weight: bold; margin: 40px 0 8px 0; letter-spacing: 1px; }}
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
    div.stButton > button p {{ 
        font-size: 16px !important; 
        font-weight: bold !important; 
        font-family: 'Times New Roman', Times, serif !important;
        color: {COLOR_NOGAL} !important;
        white-space: normal !important;
        line-height: 1.3 !important;
    }}
    div.stButton > button:hover {{ 
        border-color: {COLOR_AZUL_OXFORD} !important;
        border-bottom-color: {COLOR_AZUL_OXFORD} !important;
        background-color: #FFFDFB !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(197, 160, 89, 0.18) !important;
    }}
    
    .titulo-ley-editorial {{
        color: {COLOR_AZUL_OXFORD};
        font-size: 16px;
        font-weight: 600;
        font-family: 'Times New Roman', Times, serif;
    }}
    .subtitulo-ley-editorial {{
        color: #64748B;
        font-size: 13px;
        font-family: 'Arial', sans-serif;
        margin-top: 3px;
    }}
    
    .book-container {{
        background-color: #FFFFFF; 
        padding: 50px 60px; 
        border-radius: 4px;
        border: 1px solid #E8E5DD; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.01);
    }}
    .book-title-header {{ color: {COLOR_AZUL_OXFORD}; font-family: 'Times New Roman', serif; font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 35px; letter-spacing: 0.5px; }}
    .book-text {{ font-family: 'Georgia', serif; color: #1E293B; font-size: 18px; line-height: 1.9; text-align: justify; white-space: pre-wrap; }}
    
    .target-active-marker {{
        background-color: {COLOR_DORADO_MUTED} !important; color: #FFFFFF !important; font-weight: bold; 
        padding: 2px 4px; border-radius: 2px; display: inline-block;
        scroll-margin-top: 140px;
    }}
    .highlight-word {{ background-color: #FEF08A; color: #000000; padding: 2px 3px; border-radius: 2px; }}
    
    [data-testid="stHeader"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- PANEL DE MEMORIA INTERNA ---
if 'view' not in st.session_state: st.session_state.view = "inicio"
if 'selected_materia' not in st.session_state: st.session_state.selected_materia = None
if 'selected_doc' not in st.session_state: st.session_state.selected_doc = None
if 'global_search_term' not in st.session_state: st.session_state.global_search_term = ""
if 'current_match_index' not in st.session_state: st.session_state.current_match_index = 0

def navegar_a(vista, materia=None, doc=None):
    st.session_state.view = vista
    st.session_state.selected_materia = materia
    st.session_state.selected_doc = doc
    st.session_state.current_match_index = 0
    st.rerun()

# --- CALLBACKS DE NAVEGACIÓN ---
def click_siguiente(total):
    if total > 0:
        st.session_state.current_match_index = (st.session_state.current_match_index + 1) % total

def click_anterior(total):
    if total > 0:
        st.session_state.current_match_index = (st.session_state.current_match_index - 1) % total

def click_limpiar():
    st.session_state.global_search_term = ""
    st.session_state.current_match_index = 0

# --- HEADER GENERAL CORPORATIVO ---
st.markdown(f"""
    <div style="margin-top:15px; border-bottom:1px solid #E8E5DD; padding-bottom:14px; margin-bottom: 30px;">
        <span class="brand-title">BORGES & LAWTON</span><br>
        <span class="brand-subtitle">Inteligencia Legal Aplicada</span>
    </div>
""", unsafe_allow_html=True)


# =========================================================
# VISTA 1: ÍNDICE DE MATERIAS
# =========================================================
if st.session_state.view == "inicio":
    st.markdown('<div class="main-header">REPOSITORIO JURÍDICO INTERNO</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subheader">Consulte los textos normativos vigentes clasificados por área de práctica profesional</div>', unsafe_allow_html=True)
    
    materias_lista = [
        "Civil, Mercantil y Registral", "Laboral y Seguridad Social",
        "Tributario y Financiero", "Químicos, Minas y Energía",
        "Petróleo", "Constitucional", "Penal", "Menores y Mujeres"
    ]
    
    cols = st.columns(4)
    for idx, materia_nombre in enumerate(materias_lista):
        with cols[idx % 4]:
            icono_materia = DICT_ICONOS.get(materia_nombre, "")
            st.markdown(icono_materia, unsafe_allow_html=True)
            if st.button(materia_nombre, key=f"materia_btn_{idx}", use_container_width=True):
                st.session_state.global_search_term = ""
                navegar_a("explorar", materia=materia_nombre)


# =========================================================
# VISTA 2: LISTADO DE LEYES
# =========================================================
elif st.session_state.view == "explorar":
    st.markdown(f"### 📂 Especialidad / {st.session_state.selected_materia}")
    if st.button("← Volver al Índice Principal", key="btn_regresar_home"): 
        navegar_a("inicio")
    
    st.markdown("<br>", unsafe_allow_html=True)
    search_query = st.text_input("Filtrar ordenamiento legal por palabra clave:", value=st.session_state.global_search_term)
    st.session_state.global_search_term = search_query
    st.markdown("---")

    if os.path.exists('borges_lawton_legal.db'):
        conn = sqlite3.connect('borges_lawton_legal.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, contenido FROM leyes WHERE materia LIKE ?", [f"%{st.session_state.selected_materia}%"])
        todas_las_leyes = cursor.fetchall()
        conn.close()
        
        st.markdown("""
            <div style="display:flex; justify-content:space-between; padding: 10px 5px; font-weight:bold; color:#64748B; font-size:12px; border-bottom:2px solid #E2E8F0; font-family:'Arial'; text-transform:uppercase; letter-spacing:1px;">
                <span>Cuerpo Legal del Documento</span>
                <span style="margin-right:45px;">Acceso</span>
            </div>
        """, unsafe_allow_html=True)
        
        if not todas_las_leyes:
            st.info("No se encontraron registros para la materia seleccionada.")
        else:
            for id_ley, titulo, contenido in todas_las_leyes:
                col_texto, col_accion = st.columns([8.2, 1.8])
                with col_texto:
                    st.markdown(f"""
                        <div style="padding: 10px 0;">
                            <div class="titulo-ley-editorial">📄 {titulo}</div>
                            <div class="subtitulo-ley-editorial">Texto oficial digitalizado y verificado</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col_accion:
                    st.markdown('<div style="padding-top:14px;">', unsafe_allow_html=True)
                    if st.button("Abrir Texto", key=f"open_law_{id_ley}", use_container_width=True):
                        navegar_a("lectura", materia=st.session_state.selected_materia, doc=(titulo, contenido))
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div style="border-bottom: 1px solid #E8E5DD; margin-top:2px;"></div>', unsafe_allow_html=True)


# =========================================================
# VISTA 3: VISOR DE LEY CON MOTOR DE SALTO
# =========================================================
elif st.session_state.view == "lectura":
    titulo_doc, contenido_completo = st.session_state.selected_doc
    
    num_coincidencias = 0
    todas_las_coincidencias = []
    texto_a_mostrar = contenido_completo
    
    if st.session_state.global_search_term.strip():
        def mapear_regex(char):
            c = char.lower()
            if c in 'aá': return '[aáAÁ]'
            if c in 'eé': return '[eéEÉ]'
            if c in 'ií': return '[iíIÍ]'
            if c in 'oó': return '[oóOÓ]'
            if c in 'uúü': return '[uúüUÚÜ]'
            return re.escape(char)

        palabra_limpia = remover_acentos(st.session_state.global_search_term.strip())
        patron_regex = "".join(mapear_regex(c) for c in palabra_limpia)
        todas_las_coincidencias = list(re.finditer(patron_regex, contenido_completo))
        num_coincidencias = len(todas_las_coincidencias)

    # BARRA DE ESCANEO A LA IZQUIERDA
    with st.sidebar:
        st.markdown(f"### 🔍 Navegación")
        if st.button("⬅️ Cerrar Ley Actual", use_container_width=True, key="btn_close_law"):
            navegar_a("explorar", materia=st.session_state.selected_materia)
            
        st.markdown("---")
        
        palabra_interna = st.text_input("Término a escanear:", value=st.session_state.global_search_term, placeholder="Buscar palabra clave...")
        if palabra_interna != st.session_state.global_search_term:
            st.session_state.global_search_term = palabra_interna
            st.session_state.current_match_index = 0
            st.rerun()
            
        if st.button("Limpiar Filtro", use_container_width=True, key="btn_clear_search"):
            click_limpiar()
            st.rerun()
            
        st.markdown("---")
        
        if num_coincidencias > 0:
            st.markdown(f"**Coincidencia:** {st.session_state.current_match_index + 1} de {num_coincidencias}")
            
            col_ant, col_sig = st.columns(2)
            with col_ant:
                st.button("⏮️ Anterior", use_container_width=True, key="sidebar_btn_ant", on_click=click_anterior, args=(num_coincidencias,))
            with col_sig:
                st.button("Siguiente ⏭️", use_container_width=True, key="sidebar_btn_sig", on_click=click_siguiente, args=(num_coincidencias,))
        else:
            if st.session_state.global_search_term.strip():
                st.warning("No se hallaron coincidencias.")
            else:
                st.info("Escriba un término para resaltar pasajes jurídicos.")

    # PROCESAMIENTO DEL TEXTO RESALTADO
    if num_coincidencias > 0:
        piezas = []
        ultimo_indice = 0
        for i, match in enumerate(todas_las_coincidencias):
            start, end = match.start(), match.end()
            piezas.append(contenido_completo[ultimo_indice:start])
            texto_original_hallado = contenido_completo[start:end]
            
            if i == st.session_state.current_match_index:
                piezas.append(f'<span class="target-active-marker" id="active-target-jump">{texto_original_hallado}</span>')
            else:
                piezas.append(f'<span class="highlight-word">{texto_original_hallado}</span>')
            ultimo_indice = end
        piezas.append(contenido_completo[ultimo_indice:])
        texto_a_mostrar = "".join(piezas)
        
        st.components.v1.html(f"""
            <script>
                setTimeout(function() {{
                    var domParent = window.parent.document;
                    var target = domParent.getElementById("active-target-jump");
                    if (target) {{
                        target.scrollIntoView({{ behavior: "auto", block: "center" }});
                    }}
                }}, 150);
            </script>
        """, height=0, width=0)

    # TEXTO DE LA NORMA
    st.markdown(f"""
        <div class="book-container">
            <div class="book-title-header">{titulo_doc.upper()}</div>
            <div class="book-text">{texto_a_mostrar}</div>
        </div>
    """, unsafe_allow_html=True)