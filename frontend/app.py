import json
import os
import requests
import streamlit as st
import io
from fpdf import FPDF
from streamlit_lottie import st_lottie

# ==========================================
# 📐 CONFIGURACIÓN TÁCTIL E INTERACTIVA (Redmi Pad / Tablet)
# ==========================================
st.set_page_config(
    page_title="Historias que Inspiran® | Plataforma de Emprendimiento",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS Personalizados para Simular Experiencia de App/Videojuego
st.markdown(
    """
<style>
    /* Estilo del contenedor principal */
    .stApp {
        background-color: #0B131F;
        color: #F3F4F6;
    }
    
    /* Botones estilo Videojuego */
    .stButton>button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        padding: 12px 24px;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(16, 185, 129, 0.55);
    }

    /* Tarjetas Interactivas de Mundos */
    .world-card {
        background: #1E293B;
        border-radius: 20px;
        padding: 20px;
        border: 2px solid #334155;
        text-align: center;
        transition: transform 0.2s;
    }
    
    /* Burbuja de Chat Dudi / XiXi */
    .chat-bubble-xixi {
        background-color: #1E293B;
        border-left: 5px solid #00FFCC;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    
    .chat-bubble-dudi {
        background-color: #334155;
        border-left: 5px solid #F43F5E;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 📍 ENRUTAMIENTO DE ENTORNO E INICIALIZACIÓN
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


# ==========================================
# ⚡ FUNCIONES AUXILIARES OPTIMIZADAS (CACHÉ)
# ==========================================
@st.cache_data(show_spinner=False)
def cargar_lottie_local(filepath: str):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


@st.cache_data(ttl=60, show_spinner=False)
def obtener_libro_vivo_cached(api_url, usuario_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{api_url}/usuarios/{usuario_id}/libro", headers=headers)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"capitulo_actual": 1, "paginas_completadas": 0}


# ==========================================
# 🔒 SISTEMA DE AUTENTICACIÓN / LANDING INFANTIL
# ==========================================
if not st.session_state.get("autenticado", False):
    with st.sidebar:
        st.markdown("### 🔐 Acceso al Universo")
        tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])

        with tab_login:
            email_input = st.text_input(
                "Correo Electrónico", value=DEV_EMAIL, key="login_email"
            )
            password_input = st.text_input(
                "Contraseña", type="password", value=DEV_PASS, key="login_pass"
            )

            if st.button("🚀 Entrar al Juego", key="btn_login"):
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
                        st.success("¡Bienvenido Creador!")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # Landing Page de Bienvenida Visual (Pantalla 1 y 2 del Prototipo)
    st.markdown(
        """
    <div style="text-align: center; padding: 30px 10px;">
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

    col_hero1, col_hero2 = st.columns([1, 1])
    with col_hero1:
        st.markdown(
            """
        <div style="background-color: #1E293B; border-radius: 20px; padding: 25px; border: 2px solid #00FFCC;">
            <h2 style="color: #00FFCC;">👽 ¡Hola, Futuro Creador!</h2>
            <p style="font-size: 18px; line-height: 1.6;">
                Soy <b>XiXi</b>, tu compañera de aventuras. Juntos vamos a transformar tus ideas en una empresa real. 
                Aprenderemos a diseñar tu marca, crear tu logo, organizar tu dinero y compartir tu talento con el mundo.
            </p>
            <p style="font-size: 16px; color: #94A3B8;">
                <i>"Ninguna historia es igual. Cada idea tiene alma."</i>
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_hero2:
        st.markdown(
            """
        <div style="background-color: #1E293B; border-radius: 20px; padding: 25px; border: 2px solid #F43F5E;">
            <h2 style="color: #F43F5E;">☁️ ¿Dudas o Miedos? ¡Hola, Dudi!</h2>
            <p style="font-size: 18px; line-height: 1.6;">
                A veces aparecerá <b>Dudi</b> a preguntarte <i>"¿Y si me equivoco?"</i>. 
                ¡No te preocupes! En este universo aprenderemos que los errores también nos enseñan y nos hacen más fuertes.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "👈 **Abre la barra lateral de la izquierda e inicia sesión para comenzar tu aventura.**"
    )
    st.stop()

# ==========================================
# 🛡️ CABECERAS SEGURAS GLOBALES
# ==========================================
headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
usuario_id = st.session_state.usuario_id or 1

# Barra Lateral con Mantenimiento
with st.sidebar:
    st.markdown(
        f"### 👤 Creador: **{st.session_state.get('nombre_usuario', 'Rafael')}**"
    )
    st.caption(f"ID Usuario: #{usuario_id} | Conexión: Nube Segura")

    if st.button("🚪 Cerrar Sesión"):
        st.cache_data.clear()
        st.session_state.token = None
        st.session_state.usuario_id = None
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧹 Mantenimiento de Datos")
    if st.button("🔥 Reiniciar Usuario a Base Cero (0 XP)"):
        res_reset = requests.post(
            f"{API_URL}/usuarios/{usuario_id}/reset-base-cero", headers=headers
        )
        if res_reset.status_code == 200:
            st.cache_data.clear()
            st.session_state.messages = []
            st.toast("🧹 Usuario reiniciado a Base Cero (0 XP)", icon="✨")
            st.rerun()

# Obtención de Datos Reales del Usuario
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
# 🗺️ NAVEGACIÓN PRINCIPAL (MUNDOS / TABLERO)
# ==========================================
st.markdown("## 🗺️ Mapa del Mundo de los Creadores")

col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns(5)

with col_nav1:
    if st.button("🏠 Casa Founder"):
        st.session_state["menu_activo"] = "🏠 Casa del Fundador"
with col_nav2:
    if st.button("🌳 Árbol de Vida"):
        st.session_state["menu_activo"] = "🌳 Árbol de Vida"
with col_nav3:
    if st.button("🎯 Taller & IA"):
        st.session_state["menu_activo"] = "🎯 Taller Creativo & IA"
with col_nav4:
    if st.button("📖 Libro Vivo"):
        st.session_state["menu_activo"] = "📖 Libro Vivo"
with col_nav5:
    if st.button("💰 Ciudad Dinero"):
        st.session_state["menu_activo"] = "💰 Ciudad del Dinero"

st.markdown("---")

# ==========================================
# 1. CASA DEL FUNDADOR / HABITACIÓN (Pantalla 5)
# ==========================================
if st.session_state["menu_activo"] == "🏠 Casa del Fundador":
    st.markdown("### 🏡 Casa del Fundador — Tu Espacio Personal")
    st.caption(
        "Desde aquí comienza tu viaje. Revisa tus avances y prepara tu siguiente aventura."
    )

    col_casa1, col_casa2 = st.columns([2, 1])

    with col_casa1:
        st.info(
            f"✨ **¡Hola, {st.session_state.get('nombre_usuario', 'Rafael')}!** Tu Pasaporte de Creador está activo en Nivel {nivel_actual}."
        )

        # Muro de Chispas / Mascotas
        st.markdown("#### ✨ Mis Chispas Guía")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        col_c1.metric("🟡 Lumi", "Brillo", "Guía")
        col_c2.metric("💧 Brisa", "Calma", "Enfoque")
        col_c3.metric("🔥 Nova", "Inspira", "Energía")
        col_c4.metric("🌱 Eco", "Conecta", "Empatía")

    with col_casa2:
        st.markdown(
            """
        <div style="background-color: #1E293B; border-radius: 15px; padding: 20px; text-align: center; border: 2px solid #10B981;">
            <h3>📘 Pasaporte Oficial</h3>
            <p>Estado: <b>Creador Activo</b></p>
            <p>Nivel Alcanzado: <b>Nivel %d</b></p>
            <p>XP Acumulados: <b>%d pts</b></p>
        </div>
        """
            % (nivel_actual, xp_actual),
            unsafe_allow_html=True,
        )

# ==========================================
# 2. ÁRBOL DE VIDA (Pantalla 6)
# ==========================================
elif st.session_state["menu_activo"] == "🌳 Árbol de Vida":
    st.markdown("### 🌳 Árbol de Vida — Bio-Estructura en Crecimiento")
    st.caption(
        "Tu árbol crece con tus habilidades, proyectos y valores, no solo con dinero."
    )

    col_arb1, col_arb2 = st.columns([1, 2])

    with col_arb1:
        st.markdown(
            "<h1 style='text-align: center; font-size: 90px;'>🌳</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h3 style='text-align: center; color: #10B981;'>Fase: {estado_arbol.upper()}</h3>",
            unsafe_allow_html=True,
        )

    with col_arb2:
        xp_inicio = (nivel_actual - 1) * 100
        xp_fin = nivel_actual * 100
        xp_faltantes = max(0, xp_fin - xp_actual)
        progreso = min(1.0, max(0.0, (xp_actual - xp_inicio) / 100))

        st.metric(
            "Nivel Actual de Creador",
            f"Nivel {nivel_actual}",
            f"{xp_actual} XP Totales",
        )
        st.progress(progreso)
        st.caption(
            f"🚀 Te faltan {xp_faltantes} XP para evolucionar al Nivel {nivel_actual + 1}"
        )

        st.markdown("#### 🏅 Insignias Acreditadas")
        st.write("🛸 Primer Contacto | 🏅 Brote Explorador | 🌳 Líder Enraizado")

# ==========================================
# 3. TALLER CREATIVO & LABORATORIO IA (Pantallas 11, 12, 9 y 10)
# ==========================================
elif st.session_state["menu_activo"] == "🎯 Taller Creativo & IA":
    st.markdown("### 🎯 Laboratorio IA & Taller Creativo")
    st.caption(
        "Interactúa con XiXi para crear tu empresa o conversa con Dudi si tienes alguna duda."
    )

    tab_xixi, tab_dudi, tab_misión = st.tabs(
        ["👽 Conversar con XiXi", "☁️ Hablar con Dudi (Dudas)", "🎯 Misión del Día"]
    )

    # TAB XIXI
    with tab_xixi:
        st.markdown("#### 👽 Asistente IA de Emprendimiento (XiXi)")

        # Selector de Rol Operativo
        rol_ui = st.radio(
            "Selecciona el enfoque de tu consulta:",
            [
                "🎨 Crear Marca y Logo (Brote)",
                "📜 Definir Misión/Visión (Árbol)",
                "💰 Guía Financiera (Frondoso)",
            ],
            horizontal=True,
        )
        map_roles = {
            "🎨 Crear Marca y Logo (Brote)": "brote",
            "📜 Definir Misión/Visión (Árbol)": "arbol",
            "💰 Guía Financiera (Frondoso)": "finanzas",
        }
        rol_activo = map_roles[rol_ui]

        for msg in st.session_state.messages:
            avatar = "🧑‍🎓" if msg["role"] == "user" else "👽"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Pregúntale a XiXi sobre tu empresa..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="👽"):
                with st.spinner("XiXi está canalizando tu idea de negocio..."):
                    payload = {
                        "personaje": "xixi",
                        "mensaje_usuario": prompt,
                        "respuesta_guia": "",
                        "rol_activo": rol_activo,
                    }
                    res_chat = requests.post(
                        f"{API_URL}/usuarios/{usuario_id}/interacciones/",
                        json=payload,
                        headers=headers,
                    )
                    if res_chat.status_code == 201:
                        datos = res_chat.json()
                        resp = datos.get("respuesta_guia", "Conexión galáctica lista.")
                        xp_g = datos.get("xp_ganado", 25)

                        msg_fmt = f"{resp}\n\n*(XiXi te ha otorgado **+{xp_g} XP**)*"
                        st.markdown(msg_fmt)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": msg_fmt}
                        )
                        st.rerun()

    # TAB DUDI (Gestión Emocional)
    with tab_dudi:
        st.markdown("#### ☁️ Dudi — Tu Voz de la Duda")
        st.caption(
            "Tener dudas o miedo a equivocarse es completamente normal. ¡Exprésalo aquí!"
        )

        st.markdown(
            """
        <div class="chat-bubble-dudi">
            <b>☁️ Dudi dice:</b> <i>"¿Y si mi idea de empresa no le gusta a nadie?"</i>
        </div>
        <div class="chat-bubble-xixi">
            <b>👽 XiXi responde:</b> <i>"¡Tranquilo! Todos los grandes creadores dudaron al principio. Cada intento te enseña a mejorar."</i>
        </div>
        """,
            unsafe_allow_html=True,
        )

        duda_input = st.text_input("¿Qué duda o temor tienes hoy?")
        if st.button("💬 Resolver mi duda con XiXi"):
            if duda_input:
                st.success(
                    f"✨ XiXi dice: '¡Gracias por compartir tu duda! Reconocer el miedo con Dudi es el primer paso para ser un emprendedor valiente.'"
                )

    # TAB MISIÓN
    with tab_misión:
        st.markdown("#### 🎯 Generar Misión de Emprendimiento con IA")
        if st.button("🛸 Solicitar Nueva Misión a XiXi"):
            res_ia = requests.post(
                f"{API_URL}/usuarios/{usuario_id}/misiones/generar_ia?enfoque=emprendimiento",
                headers=headers,
            )
            if res_ia.status_code in [200, 201]:
                st.toast("✨ ¡Nueva Misión encomendada por XiXi!", icon="🎯")
                st.rerun()

        # Listado de Misiones
        res_m = requests.get(
            f"{API_URL}/usuarios/{usuario_id}/misiones/", headers=headers
        )
        if res_m.status_code == 200:
            misiones_list = [m for m in res_m.json() if m.get("estado") == "pendiente"]
            for m in misiones_list:
                m_id = m.get("id")
                st.markdown(
                    f"**{m.get('titulo_mision')}** (+{m.get('recompensa_puntos')} XP)"
                )
                st.caption(m.get("descripcion"))
                if st.button(f"Completar Misión #{m_id}", key=f"btn_mis_{m_id}"):
                    res_c = requests.put(
                        f"{API_URL}/usuarios/{usuario_id}/misiones/{m_id}/completar",
                        headers=headers,
                    )
                    if res_c.status_code == 200:
                        st.balloons()
                        st.toast("🎉 ¡Misión completada! XP asignados.", icon="🚀")
                        st.rerun()

# ==========================================
# 4. LIBRO VIVO (Pantalla 7)
# ==========================================
elif st.session_state["menu_activo"] == "📖 Libro Vivo":
    st.markdown("### 📖 El Libro Vivo de tu Empresa")
    st.caption(
        "Esta es tu autobiografía interactiva. Aquí se guardan automáticamente tus logros y reflexiones."
    )

    datos_libro = obtener_libro_vivo_cached(API_URL, usuario_id, st.session_state.token)
    cap = datos_libro.get("capitulo_actual", 1)
    pag = datos_libro.get("paginas_completadas", 0)

    st.markdown(f"#### 📜 Capítulo {cap}: La Bitácora del Creador")
    st.write(f"**Páginas escritas:** {'📄 ' * pag}{'▫️ ' * (5 - pag)}")

    res_m = requests.get(f"{API_URL}/usuarios/{usuario_id}/misiones/", headers=headers)
    if res_m.status_code == 200:
        completadas = [m for m in res_m.json() if m.get("estado") == "completada"]
        for i, m in enumerate(completadas, start=1):
            st.markdown(
                f"""
            <div style="background-color: #1E293B; border-radius: 10px; padding: 12px; margin-bottom: 10px; border-left: 4px solid #10B981;">
                <span style="color: #00FFCC; font-weight: bold;">📄 Página {i}:</span> 
                <span style="color: #F3F4F6;">Hito Alcanzado — {m.get("titulo_mision")}</span><br>
                <span style="color: #9CA3AF; font-style: italic;">"{m.get("descripcion")}"</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ==========================================
# 5. CIUDAD DEL DINERO (Pantalla 14)
# ==========================================
elif st.session_state["menu_activo"] == "💰 Ciudad del Dinero":
    st.markdown("### 💰 Ciudad del Dinero — Educación Financiera")
    st.caption(
        "Aprende a manejar los recursos de tu empresa con inteligencia y visión de futuro."
    )

    col_fin1, col_fin2, col_fin3 = st.columns(3)
    with col_fin1:
        st.markdown(
            """
        <div style="background-color: #1E293B; border-radius: 15px; padding: 20px; text-align: center; border-top: 5px solid #10B981;">
            <h2>🪙 Ganar</h2>
            <p>Calcula el precio de tus productos o servicios.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_fin2:
        st.markdown(
            """
        <div style="background-color: #1E293B; border-radius: 15px; padding: 20px; text-align: center; border-top: 5px solid #38BDF8;">
            <h2>🐖 Ahorrar</h2>
            <p>Guarda una parte de tus ganancias para crecer.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_fin3:
        st.markdown(
            """
        <div style="background-color: #1E293B; border-radius: 15px; padding: 20px; text-align: center; border-top: 5px solid #F59E0B;">
            <h2>🌱 Reinvertir</h2>
            <p>Compra nuevos materiales para mejorar tu marca.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.metric("💰 Tu Monedero Virtual de Creador", "250 Monedas", "+50 hoy")
