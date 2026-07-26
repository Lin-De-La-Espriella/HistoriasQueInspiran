import json
import os
import requests
import streamlit as st

# ==========================================
# 📐 CONFIGURACIÓN VISUAL Y TÁCTIL (Tablet Redmi Pad)
# ==========================================
st.set_page_config(
    page_title="Historias que Inspiran® | Universo del Creador",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos CSS Personalizados estilo App Infantil
st.markdown(
    """
<style>
    .stApp {
        background-color: #0B131F;
        color: #F3F4F6;
    }
    
    /* Tarjetas del Flujo Ilustrado */
    .hero-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 24px;
        padding: 30px;
        border: 2px solid #00FFCC;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 255, 204, 0.2);
        margin-bottom: 20px;
    }

    .avatar-card {
        background-color: #1E293B;
        border-radius: 18px;
        padding: 15px;
        text-align: center;
        border: 2px solid #334155;
        transition: transform 0.2s;
    }

    .passport-card {
        background: linear-gradient(135deg, #064E3B 0%, #022C22 100%);
        border-radius: 20px;
        padding: 25px;
        border: 3px solid #10B981;
        text-align: center;
        color: #F3F4F6;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 📍 ESTADOS GLOBALES DE LA AVENTURA
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
if "paso_onboarding" not in st.session_state:
    st.session_state["paso_onboarding"] = (
        1  # 1: Splash, 2: XiXi, 3: Avatar, 4: Pasaporte, 5: Juego
    )
if "avatar_elegido" not in st.session_state:
    st.session_state["avatar_elegido"] = "👦 Rafa"
if "menu_activo" not in st.session_state:
    st.session_state["menu_activo"] = "🏠 Casa del Fundador"
if "nombre_empresa" not in st.session_state:
    st.session_state["nombre_empresa"] = "Mi Empresa Mágica"
if "eslogan_empresa" not in st.session_state:
    st.session_state["eslogan_empresa"] = "Hecho para inspirar."

# ==========================================
# 🔒 AUTENTICACIÓN
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

    # Landing Page
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
    st.info("👈 Abre el menú lateral izquierdo e inicia sesión para empezar.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
usuario_id = st.session_state.usuario_id or 1

# Barra Lateral
with st.sidebar:
    st.markdown(
        f"### 👤 Creador: **{st.session_state.get('nombre_usuario', 'Rafael')}**"
    )
    if st.button("🚪 Cerrar Sesión"):
        st.cache_data.clear()
        st.session_state.token = None
        st.session_state.usuario_id = None
        st.session_state.paso_onboarding = 1
        st.rerun()

    st.markdown("---")
    if st.button("🔥 Reiniciar Aventura desde Cero"):
        res_reset = requests.post(
            f"{API_URL}/usuarios/{usuario_id}/reset-base-cero", headers=headers
        )
        st.session_state.paso_onboarding = 1
        st.toast("🧹 Aventura reiniciada al inicio", icon="✨")
        st.rerun()

# ==========================================
# 🎮 FLUJO DIDÁCTICO DE BIENVENIDA (PANTALLAS 1 A 4)
# ==========================================
if st.session_state["paso_onboarding"] < 5:
    # PANTALLA 1: SPLASH SCREEN
    if st.session_state["paso_onboarding"] == 1:
        st.markdown(
            """
        <div class="hero-card">
            <h1 style="font-size: 70px; margin: 0;">🌳</h1>
            <h1 style="color: #00FFCC; font-size: 42px;">1. SPLASH SCREEN</h1>
            <h2 style="color: #F3F4F6;">Historias que Inspiran®</h2>
            <p style="font-size: 20px; color: #94A3B8;">
                <i>"Donde tus ideas se convierten en historias que cambian el mundo."</i>
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("🚀 Comenzar Mi Aventura ✨", key="btn_p1", type="primary"):
            st.session_state["paso_onboarding"] = 2
            st.rerun()

    # PANTALLA 2: BIENVENIDA DE XIXI
    elif st.session_state["paso_onboarding"] == 2:
        st.markdown(
            """
        <div class="hero-card" style="border-color: #38BDF8;">
            <h1 style="font-size: 70px; margin: 0;">👽</h1>
            <h1 style="color: #38BDF8; font-size: 42px;">2. BIENVENIDA DE XIXI</h1>
            <p style="font-size: 22px; color: #F3F4F6;">
                ¡Hola! Soy <b>XiXi</b>, tu compañera de aventuras galácticas.Estoy aquí para ayudarte a descubrir tu potencial y crear cosas increíbles.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("⬅️ Volver", key="btn_p2_back"):
                st.session_state["paso_onboarding"] = 1
                st.rerun()
        with col_b2:
            if st.button("Elegir Mi Avatar 🎨 ➡️", key="btn_p2_next", type="primary"):
                st.session_state["paso_onboarding"] = 3
                st.rerun()

    # PANTALLA 3: CREACIÓN DE AVATAR (GRID DE OPCIONES)
    elif st.session_state["paso_onboarding"] == 3:
        st.markdown(
            """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #A855F7;">🎨 3. CREACIÓN DE AVATAR</h1>
            <h3>Elige un avatar que te represente:</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        avatares = [
            ("👦 Rafa", "Explorador"),
            ("👧 Sofía", "Creativa"),
            ("🧑‍🎨 Tomás", "Artista"),
            ("👧 Ivonne", "Líder"),
            ("👦 Mateo", "Innovador"),
            ("👧 Camila", "Soñadora"),
            ("👦 Lucas", "Constructor"),
            ("👧 Valentina", "Empática"),
            ("👦 Diego", "Visionario"),
        ]

        cols = st.columns(3)
        for idx, (nombre_av, rol_av) in enumerate(avatares):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                <div class="avatar-card">
                    <h2 style="margin:0;">{nombre_av.split()[0]}</h2>
                    <h4>{nombre_av.split()[1]}</h4>
                    <p style="color: #94A3B8;">{rol_av}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Seleccionar {nombre_av.split()[1]}", key=f"av_{idx}"):
                    st.session_state["avatar_elegido"] = nombre_av
                    st.toast(f"¡Avatar elegido: {nombre_av}!", icon="✨")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info(
            f"✨ **Avatar Actual Seleccionado:** `{st.session_state['avatar_elegido']}`"
        )

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("⬅️ Atrás", key="btn_p3_back"):
                st.session_state["paso_onboarding"] = 2
                st.rerun()
        with col_c2:
            if st.button("Ver Mi Pasaporte 📘 ➡️", key="btn_p3_next", type="primary"):
                st.session_state["paso_onboarding"] = 4
                st.rerun()

    # PANTALLA 4: PASAPORTE DEL CREADOR
    elif st.session_state["paso_onboarding"] == 4:
        st.markdown(
            f"""
        <div class="passport-card">
            <h1 style="font-size: 60px; margin: 0;">📘</h1>
            <h1 style="color: #00FFCC; font-size: 36px;">4. PASAPORTE DEL CREADOR</h1>
            <p style="font-size: 18px;">Este es tu documento oficial como creador de historias y empresas.</p>
            <hr style="border-color: #10B981;">
            <h2>Creador: {st.session_state.get("nombre_usuario", "Rafael")}</h2>
            <h3>Avatar Oficial: {st.session_state["avatar_elegido"]}</h3>
            <p>Nivel Inicial: <b>Nivel 1 (0 XP)</b></p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if st.button("⬅️ Cambiar Avatar", key="btn_p4_back"):
                st.session_state["paso_onboarding"] = 3
                st.rerun()
        with col_d2:
            if st.button(
                "🏡 Entrar a la Casa del Fundador 🚀", key="btn_p4_next", type="primary"
            ):
                st.session_state["paso_onboarding"] = 5
                st.balloons()
                st.rerun()

    st.stop()

# ==========================================
# 🗺️ NAVEGACIÓN Y MAPA PRINCIPAL (PANTALLA 5 EN ADELANTE)
# ==========================================
res_users = requests.get(f"{API_URL}/usuarios/", headers=headers)
user_data = None
if res_users.status_code == 200:
    user_data = next((u for u in res_users.json() if u["id"] == usuario_id), None)

pasaporte = user_data.get("pasaporte", {}) if user_data else {}
arbol = user_data.get("arbol", {}) if user_data else {}
xp_actual = pasaporte.get("puntos_experiencia", 0)
nivel_actual = (xp_actual // 100) + 1
estado_arbol = arbol.get("estado_crecimiento", "semilla")

st.markdown("## 🗺️ Mapa del Mundo de los Creadores")

# RESALTE CORREGIDO: Usamos type="primary" en la pestaña activa para destacar con luz verde/brillante
col1, col2, col3, col4, col5, col6 = st.columns(6)

mundos_lista = [
    ("🏠 Casa Founder", col1, "🏠 Casa del Fundador"),
    ("🌳 Árbol de Vida", col2, "🌳 Árbol de Vida"),
    ("🎨 Taller Marca", col3, "🎨 Taller de Marca"),
    ("🎯 Taller & IA", col4, "🎯 Taller Creativo & IA"),
    ("📖 Libro Vivo", col5, "📖 Libro Vivo"),
    ("💰 Ciudad Dinero", col6, "💰 Ciudad del Dinero"),
]

for label, col, key_nombre in mundos_lista:
    with col:
        es_act = st.session_state["menu_activo"] == key_nombre
        # type="primary" resalta el botón activo brillante, type="secondary" deja los demás neutros
        tipo_btn = "primary" if es_act else "secondary"

        if st.button(label, key=f"nav_{key_nombre}", type=tipo_btn):
            st.session_state["menu_activo"] = key_nombre
            st.rerun()

st.markdown("---")

# ==========================================
# 5. CASA DEL FUNDADOR (PANTALLA 5 REAL)
# ==========================================
if st.session_state["menu_activo"] == "🏠 Casa del Fundador":
    st.markdown("### 🏡 5. CASA DEL FUNDADOR — Tu Espacio Personal")
    st.caption("Este es tu espacio personal. Desde aquí comienza tu viaje.")

    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        st.info(
            f"✨ **¡Hola, {st.session_state.get('nombre_usuario', 'Rafael')}!** Tu aventura como creador está en curso."
        )
        st.markdown("#### ✨ Mis Chispas Guía")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("🟡 Lumi", "Brillo", "Guía")
        col_b.metric("💧 Brisa", "Calma", "Enfoque")
        col_c.metric("🔥 Nova", "Inspira", "Energía")
        col_d.metric("🌱 Eco", "Conecta", "Empatía")

    with col_c2:
        st.markdown(
            f"""
        <div class="passport-card">
            <h3>📘 Pasaporte Oficial</h3>
            <p>Creador: <b>{st.session_state.get("nombre_usuario", "Rafael")}</b></p>
            <p>Avatar: <b>{st.session_state["avatar_elegido"]}</b></p>
            <p>Nivel Actual: <b>Nivel {nivel_actual}</b></p>
            <p>XP Acumulados: <b>{xp_actual} pts</b></p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# ==========================================
# 6. ÁRBOL DE VIDA (PANTALLA 6)
# ==========================================
elif st.session_state["menu_activo"] == "🌳 Árbol de Vida":
    st.markdown("### 🌳 6. ÁRBOL DE VIDA — Crecimiento Personal")
    st.caption("Aquí crecerán tus ideas, logros y aprendizajes.")

    col_a1, col_a2 = st.columns([1, 2])
    with col_a1:
        st.markdown(
            "<h1 style='text-align: center; font-size: 90px;'>🌳</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h3 style='text-align: center; color: #10B981;'>Fase: {estado_arbol.upper()}</h3>",
            unsafe_allow_html=True,
        )
    with col_a2:
        st.metric("Nivel Actual", f"Nivel {nivel_actual}", f"{xp_actual} XP Totales")
        st.progress(min(1.0, (xp_actual % 100) / 100))

# ==========================================
# 7. TALLER DE MARCA (MUNDO BROTE)
# ==========================================
elif st.session_state["menu_activo"] == "🎨 Taller de Marca":
    st.markdown("### 🎨 Taller de Identidad de Marca")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        empresa_in = st.text_input(
            "Nombre de la Empresa", value=st.session_state["nombre_empresa"]
        )
        eslogan_in = st.text_input("Eslogan", value=st.session_state["eslogan_empresa"])
        if st.button("💾 Guardar Marca", type="primary"):
            st.session_state["nombre_empresa"] = empresa_in
            st.session_state["eslogan_empresa"] = eslogan_in
            st.toast("🎉 ¡Marca registrada!", icon="✨")
    with col_m2:
        st.markdown(
            f"""
        <div class="hero-card">
            <h1 style="color: #00FFCC;">🚀 {st.session_state["nombre_empresa"]}</h1>
            <p style="font-size: 18px;">"{st.session_state["eslogan_empresa"]}"</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# ==========================================
# 8. TALLER CREATIVO & IA
# ==========================================
elif st.session_state["menu_activo"] == "🎯 Taller Creativo & IA":
    st.markdown("### 🎯 Laboratorio IA & Taller Creativo")
    tab_xixi, tab_dudi = st.tabs(["👽 Guía de XiXi", "☁️ Conversar con Dudi"])

    with tab_xixi:
        st.markdown("#### 👽 XiXi te acompaña a crear tu empresa")
        prompt = st.text_input("Escribe tu idea o pregunta para XiXi:")
        if st.button("🚀 Enviar a XiXi", type="primary"):
            if prompt:
                st.success(
                    "✨ XiXi dice: '¡Fantástica idea! Daremos el siguiente paso juntos.'"
                )

    with tab_dudi:
        st.markdown("#### ☁️ Conversación con Dudi (Gestión de Dudas)")
        st.info(
            "☁️ Dudi: '¿Y si no soy bueno en esto?' | 👽 XiXi: '¡Voy a intentarlo de todas formas!'"
        )

# ==========================================
# 9. LIBRO VIVO (PANTALLA 7)
# ==========================================
elif st.session_state["menu_activo"] == "📖 Libro Vivo":
    st.markdown("### 📖 El Libro Vivo de tu Empresa")
    st.caption("Aquí guardas tus historias, reflexiones y aprendizajes.")
    st.markdown(f"**Empresa Registrada:** {st.session_state['nombre_empresa']}")

# ==========================================
# 10. CIUDAD DEL DINERO (PANTALLA 14)
# ==========================================
elif st.session_state["menu_activo"] == "💰 Ciudad del Dinero":
    st.markdown("### 💰 Ciudad del Dinero — Educación Financiera")
    st.caption("Aprende a manejar tus recursos y haz crecer tus ideas.")
