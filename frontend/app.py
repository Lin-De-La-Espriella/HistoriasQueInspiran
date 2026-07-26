import json
import os
import requests
import streamlit as st
import io
from fpdf import FPDF

# ==========================================
# 📐 CONFIGURACIÓN TÁCTIL Y VISUAL (Redmi Pad / Tablet)
# ==========================================
st.set_page_config(
    page_title="Historias que Inspiran® | Ecosistema Didáctico",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos CSS Personalizados: Resalte Neón + Opacidad de Pestañas
st.markdown(
    """
<style>
    .stApp {
        background-color: #0B131F;
        color: #F3F4F6;
    }
    
    /* Botones estándar */
    .stButton>button {
        background: #1E293B;
        color: #94A3B8;
        font-weight: bold;
        border-radius: 12px;
        border: 2px solid #334155;
        padding: 10px 18px;
        transition: all 0.3s ease;
        width: 100%;
        opacity: 0.45; /* Opaque para inactivos */
    }
    
    /* Pestaña Activa Resaltada con Brillo Neón */
    .active-world button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #00FFCC !important;
        box-shadow: 0 0 20px #00FFCC !important;
        opacity: 1.0 !important; /* Totalmente visible */
        transform: scale(1.05);
    }

    /* Tarjetas Interactivas de Rutas */
    .route-card {
        background-color: #1E293B;
        border-radius: 20px;
        padding: 20px;
        border: 2px solid #38BDF8;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.2);
        margin-bottom: 20px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 📍 ENRUTAMIENTO Y ESTADOS GLOBALES
# ==========================================
API_URL = "https://historias-que-inspiran-api.onrender.com"
DEV_EMAIL = "lindley@historias.com"
DEV_PASS = "superPassword123"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None
if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "menu_activo" not in st.session_state:
    st.session_state["menu_activo"] = "🏠 Casa del Fundador"

# Estados de la Aventura Didáctica Infantil
if "avatar_elegido" not in st.session_state:
    st.session_state["avatar_elegido"] = "👦 Rafa"
if "ruta_negocio" not in st.session_state:
    st.session_state["ruta_negocio"] = None
if "nombre_empresa" not in st.session_state:
    st.session_state["nombre_empresa"] = "Mi Empresa Mágica"
if "eslogan_empresa" not in st.session_state:
    st.session_state["eslogan_empresa"] = "Hecho para inspirar."

# ==========================================
# 🔒 AUTENTICACIÓN Y PANTALLA BIENVENIDA
# ==========================================
if not st.session_state.get("autenticado", False):
    with st.sidebar:
        st.markdown("### 🔐 Acceso al Universo")
        email_input = st.text_input("Correo", value=DEV_EMAIL)
        password_input = st.text_input("Contraseña", type="password", value=DEV_PASS)

        if st.button("🚀 Entrar al Juego"):
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email_input, "password": password_input},
                )
                if response.status_code == 200:
                    data_token = response.json()
                    st.session_state["token"] = data_token.get("access_token")
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_id"] = data_token.get("usuario_id", 1)
                    st.session_state["nombre_usuario"] = data_token.get(
                        "nombre", "Rafael"
                    )
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Landing Page Ilustrada
    st.markdown(
        """
    <div style="text-align: center; padding: 20px;">
        <h1 style="font-size: 48px; color: #00FFCC; font-weight: 900;">
            🌱 HISTORIAS QUE INSPIRAN®
        </h1>
        <p style="font-size: 22px; color: #E2E8F0;">
            Descubre tu talento. Crea soluciones. Inspira al mundo. 🚀
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown(
            """
        <div class="route-card" style="border-color: #00FFCC;">
            <h2 style="color: #00FFCC;">👽 ¡Bienvenido con XiXi!</h2>
            <p style="font-size: 18px;">Acompaña a XiXi a explorar mundos y crear tu propia empresa desde cero.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown(
            """
        <div class="route-card" style="border-color: #F43F5E;">
            <h2 style="color: #F43F5E;">☁️ Abraza tus dudas con Dudi</h2>
            <p style="font-size: 18px;">Tener miedo o dudas es normal. ¡Juntos aprenderemos a superar cada reto!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.info("👈 Abre el menú lateral izquierdo e inicia sesión para empezar.")
    st.stop()

# ==========================================
# 🛡️ CABECERAS SEGURAS GLOBALES
# ==========================================
headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
usuario_id = st.session_state.usuario_id or 1

with st.sidebar:
    st.markdown(
        f"### 👤 Creador: **{st.session_state.get('nombre_usuario', 'Rafael')}**"
    )
    if st.button("🚪 Cerrar Sesión"):
        st.cache_data.clear()
        st.session_state.token = None
        st.session_state.usuario_id = None
        st.session_state.messages = []
        st.rerun()

res_users = requests.get(f"{API_URL}/usuarios/", headers=headers)
user_data = None
if res_users.status_code == 200:
    user_data = next((u for u in res_users.json() if u["id"] == usuario_id), None)

pasaporte = user_data.get("pasaporte", {}) if user_data else {}
arbol = user_data.get("arbol", {}) if user_data else {}
xp_actual = pasaporte.get("puntos_experiencia", 0)
nivel_actual = (xp_actual // 100) + 1
estado_arbol = arbol.get("estado_crecimiento", "semilla")

# ==========================================
# 🗺️ MAPA CON RESALTE Y OPACIDAD DINÁMICA (IMAGEN 1)
# ==========================================
st.markdown("## 🗺️ Mapa del Mundo de los Creadores")

col1, col2, col3, col4, col5, col6 = st.columns(6)

mundos = [
    ("🏠 Casa Founder", col1, "🏠 Casa del Fundador"),
    ("🌳 Árbol de Vida", col2, "🌳 Árbol de Vida"),
    ("🎨 Taller Marca", col3, "🎨 Taller de Marca"),
    ("🎯 Taller & IA", col4, "🎯 Taller Creativo & IA"),
    ("📖 Libro Vivo", col5, "📖 Libro Vivo"),
    ("💰 Ciudad Dinero", col6, "💰 Ciudad del Dinero"),
]

for label, col, key_nombre in mundos:
    with col:
        es_activo = st.session_state["menu_activo"] == key_nombre
        clase_css = "active-world" if es_activo else "inactive-world"

        # Envolvemos el botón en un contenedor div para aplicar el resalte dinámico
        st.markdown(f'<div class="{clase_css}">', unsafe_allow_html=True)
        if st.button(label, key=f"btn_map_{key_nombre}"):
            st.session_state["menu_activo"] = key_nombre
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 1. CASA DEL FUNDADOR & SELECCIÓN DE AVATAR (PANTALLAS 3, 4 y 5)
# ==========================================
if st.session_state["menu_activo"] == "🏠 Casa del Fundador":
    st.markdown("### 🏡 Casa del Fundador — Tu Espacio Personal")
    st.caption("Selecciona tu avatar de creador y revisa tu Pasaporte Oficial.")

    col_av1, col_av2 = st.columns([2, 1])

    with col_av1:
        st.markdown("#### 🎨 Elige tu Avatar que te represente (Pantalla 3)")
        col_a, col_b, col_c, col_d = st.columns(4)

        with col_a:
            st.markdown("### 👦 Rafa")
            if st.button("Elegir a Rafa"):
                st.session_state["avatar_elegido"] = "👦 Rafa"
                st.toast("¡Avatar actualizado a Rafa!", icon="✨")
        with col_b:
            st.markdown("### 👧 Sofía")
            if st.button("Elegir a Sofía"):
                st.session_state["avatar_elegido"] = "👧 Sofía"
                st.toast("¡Avatar actualizado a Sofía!", icon="✨")
        with col_c:
            st.markdown("### 🧑‍🎨 Tomás")
            if st.button("Elegir a Tomás"):
                st.session_state["avatar_elegido"] = "🧑‍🎨 Tomás"
                st.toast("¡Avatar actualizado a Tomás!", icon="✨")
        with col_d:
            st.markdown("### 👧 Ivonne")
            if st.button("Elegir a Ivonne"):
                st.session_state["avatar_elegido"] = "👧 Ivonne"
                st.toast("¡Avatar actualizado a Ivonne!", icon="✨")

        st.info(f"✨ **Avatar Seleccionado:** `{st.session_state['avatar_elegido']}`")

    with col_av2:
        st.markdown(
            f"""
        <div class="route-card" style="border-color: #10B981;">
            <h3>📘 Pasaporte del Creador</h3>
            <p>Creador: <b>{st.session_state.get("nombre_usuario", "Rafael")}</b></p>
            <p>Avatar: <b>{st.session_state["avatar_elegido"]}</b></p>
            <p>Nivel Actual: <b>Nivel {nivel_actual}</b></p>
            <p>Puntos XP: <b>{xp_actual} pts</b></p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# ==========================================
# 2. ÁRBOL DE VIDA (PANTALLA 6)
# ==========================================
elif st.session_state["menu_activo"] == "🌳 Árbol de Vida":
    st.markdown("### 🌳 Árbol de Vida — Bio-Estructura en Crecimiento")
    st.caption("Tu árbol crece con tus habilidades, proyectos y valores.")

    col_arb1, col_arb2 = st.columns([1, 2])

    with col_arb1:
        st.markdown(
            "<h1 style='text-align: center; font-size: 100px;'>🌳</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h3 style='text-align: center; color: #10B981;'>Fase: {estado_arbol.upper()}</h3>",
            unsafe_allow_html=True,
        )

    with col_arb2:
        st.metric("Nivel Actual", f"Nivel {nivel_actual}", f"{xp_actual} XP")
        progreso = min(1.0, (xp_actual % 100) / 100)
        st.progress(progreso)
        st.markdown("#### 🏅 Insignias Acreditadas")
        st.write("🛸 Primer Contacto | 🏅 Brote Explorador | 🌳 Líder Enraizado")

# ==========================================
# 3. TALLER DE MARCA (MUNDO BROTE)
# ==========================================
elif st.session_state["menu_activo"] == "🎨 Taller de Marca":
    st.markdown("### 🎨 Taller de Identidad de Marca — Mundo Brote")
    st.caption("Define la personalidad de tu empresa con XiXi.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("#### 🛠️ Datos de tu Marca")
        empresa_in = st.text_input(
            "Nombre de la Empresa", value=st.session_state["nombre_empresa"]
        )
        eslogan_in = st.text_input(
            "Eslogan / Promesa", value=st.session_state["eslogan_empresa"]
        )

        if st.button("💾 Guardar Marca"):
            st.session_state["nombre_empresa"] = empresa_in
            st.session_state["eslogan_empresa"] = eslogan_in
            st.balloons()
            st.toast("🎉 ¡Marca registrada en tu Libro Vivo!", icon="✨")

    with col_t2:
        st.markdown(
            f"""
        <div class="route-card">
            <h1 style="color: #00FFCC;">🚀 {st.session_state["nombre_empresa"]}</h1>
            <p style="font-size: 18px; font-style: italic;">"{st.session_state["eslogan_empresa"]}"</p>
            <p><b>Fundador:</b> {st.session_state.get("nombre_usuario", "Rafael")}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# ==========================================
# 4. TALLER CREATIVO & RUTAS CON IMÁGENES (PANTALLAS 8, 10, 11 Y 12)
# ==========================================
elif st.session_state["menu_activo"] == "🎯 Taller Creativo & IA":
    st.markdown("### 🎯 Laboratorio IA — Elige tu Ruta de Emprendimiento")
    st.caption("Toca la ruta que quieres explorar hoy y XiXi te guiará paso a paso.")

    # RUTA DIDÁCTICA VISUAL
    col_r1, col_r2, col_r3 = st.columns(3)

    with col_r1:
        st.markdown(
            """
        <div class="route-card" style="border-color: #10B981;">
            <h1>💡</h1>
            <h3>1. Descubrir Idea</h3>
            <p>Encuentra un problema en tu entorno y crea una solución.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Elegir Ruta: Ideas"):
            st.session_state["ruta_negocio"] = "Ideas de Negocio"
            st.toast("Ruta seleccionada: Ideas", icon="💡")

    with col_r2:
        st.markdown(
            """
        <div class="route-card" style="border-color: #A855F7;">
            <h1>🎨</h1>
            <h3>2. Diseñar Producto</h3>
            <p>Crea el boceto, materiales y presentación de tu marca.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Elegir Ruta: Diseño"):
            st.session_state["ruta_negocio"] = "Diseño de Producto"
            st.toast("Ruta seleccionada: Diseño", icon="🎨")

    with col_r3:
        st.markdown(
            """
        <div class="route-card" style="border-color: #F59E0B;">
            <h1>💰</h1>
            <h3>3. Guía Financiera</h3>
            <p>Aprende a calcular costos y fijar precios con ganancia.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Elegir Ruta: Finanzas"):
            st.session_state["ruta_negocio"] = "Educación Financiera"
            st.toast("Ruta seleccionada: Finanzas", icon="💰")

    st.markdown("---")

    # INTERACCIÓN DIDÁCTICA CON XIXI Y DUDI
    tab_xixi, tab_dudi = st.tabs(["👽 Guía de XiXi", "☁️ Hablar con Dudi"])

    with tab_xixi:
        ruta_actual = st.session_state.get("ruta_negocio", "Ideas de Negocio")
        st.markdown(f"#### 👽 XiXi te acompaña en la Ruta: **{ruta_actual}**")

        st.markdown(
            f"""
        <div style="background-color: #1E293B; border-left: 5px solid #00FFCC; padding: 15px; border-radius: 12px; margin-bottom: 15px;">
            <b>👽 XiXi dice:</b> <i>"¡Excelente elección! Para avanzar en la ruta de <b>{ruta_actual}</b>, cuéntame: ¿Qué te imaginas creando y a quién le gustaría usarlo?"</i>
        </div>
        """,
            unsafe_allow_html=True,
        )

        input_nino = st.text_area(
            "✏️ Tu respuesta para XiXi:", placeholder="Escribe aquí tu idea..."
        )
        if st.button("🚀 Enviar Respuesta a XiXi"):
            if input_nino:
                st.balloons()
                st.success(
                    "✨ XiXi dice: '¡Increíble idea! La he registrado en tu Libro Vivo. Has ganado +30 XP.'"
                )

    with tab_dudi:
        st.markdown("#### ☁️ Conversación con Dudi (Gestión de Dudas)")
        st.markdown(
            """
        <div style="background-color: #334155; border-left: 5px solid #F43F5E; padding: 15px; border-radius: 12px;">
            <b>☁️ Dudi dice:</b> <i>"¿Y si mi idea no funciona o a nadie le gusta?"</i><br><br>
            <b>👽 XiXi responde:</b> <i>"¡Tranquilo! Los errores son solo lecciones de aprendizaje. ¡Avancemos juntos!"</i>
        </div>
        """,
            unsafe_allow_html=True,
        )

# ==========================================
# 5. LIBRO VIVO (PANTALLA 7)
# ==========================================
elif st.session_state["menu_activo"] == "📖 Libro Vivo":
    st.markdown("### 📖 El Libro Vivo de tu Empresa")
    st.caption("Esta es tu autobiografía interactiva. Se escribe con tus avances.")

    st.markdown(
        f"""
    <div style="background-color: #1E293B; border-radius: 12px; padding: 15px; border-left: 4px solid #00FFCC; margin-bottom: 15px;">
        <span style="color: #00FFCC; font-weight: bold;">📄 Registro de Marca:</span><br>
        <b style="font-size: 18px;">{st.session_state["nombre_empresa"]}</b> — <i>"{st.session_state["eslogan_empresa"]}"</i>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ==========================================
# 6. CIUDAD DEL DINERO (PANTALLA 14)
# ==========================================
elif st.session_state["menu_activo"] == "💰 Ciudad del Dinero":
    st.markdown("### 💰 Ciudad del Dinero — Educación Financiera")
    st.caption("Aprende a manejar los recursos de tu empresa.")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown(
            """
        <div class="route-card" style="border-top: 5px solid #10B981;">
            <h2>🪙 Ganar</h2>
            <p>Calcula tus precios y margen de ganancia.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_f2:
        st.markdown(
            """
        <div class="route-card" style="border-top: 5px solid #38BDF8;">
            <h2>🐖 Ahorrar</h2>
            <p>Guarda recursos para hacer crecer tu marca.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_f3:
        st.markdown(
            """
        <div class="route-card" style="border-top: 5px solid #F59E0B;">
            <h2>🌱 Reinvertir</h2>
            <p>Compra nuevos materiales de creación.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
