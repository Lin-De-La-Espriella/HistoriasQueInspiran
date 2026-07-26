import os
import requests
import streamlit as st

st.set_page_config(
    page_title="Historias que Inspiran® | Universo del Creador",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0B131F;
            color: #F3F4F6;
        }
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
        .section-box {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 14px;
        }
        .small-label {
            color: #94A3B8;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

API_URL = os.getenv("FRONTEND_API_URL", "http://localhost:8000")
DEV_EMAIL = os.getenv("DEV_EMAIL", "lindley@historias.com")
DEV_PASS = os.getenv("DEV_PASS", "superPassword123")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None
if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = None
if "nombre_usuario" not in st.session_state:
    st.session_state["nombre_usuario"] = "Rafael"
if "paso_onboarding" not in st.session_state:
    st.session_state["paso_onboarding"] = 1
if "avatar_elegido" not in st.session_state:
    st.session_state["avatar_elegido"] = "👦 Rafa"
if "menu_activo" not in st.session_state:
    st.session_state["menu_activo"] = "🏠 Casa del Fundador"
if "nombre_empresa" not in st.session_state:
    st.session_state["nombre_empresa"] = "Mi Empresa Mágica"
if "eslogan_empresa" not in st.session_state:
    st.session_state["eslogan_empresa"] = "Hecho para inspirar."


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def _safe_get_json(url: str, headers=None, default=None):
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return default


def _safe_post_json(url: str, payload=None, headers=None, default=None):
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            return r.json()
        st.error(r.json().get("detail", "No se pudo completar la acción"))
    except Exception as e:
        st.error(f"Error: {e}")
    return default


def _safe_put_json(url: str, payload=None, headers=None, default=None):
    try:
        r = requests.put(url, json=payload, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            return r.json()
        st.error(r.json().get("detail", "No se pudo completar la acción"))
    except Exception as e:
        st.error(f"Error: {e}")
    return default


# =========================
# AUTENTICACIÓN
# =========================
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
                    timeout=30,
                )
                if response.status_code == 200:
                    data_token = response.json()
                    st.session_state["token"] = data_token.get("access_token")
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_id"] = data_token.get("usuario_id")
                    st.session_state["nombre_usuario"] = data_token.get(
                        "nombre", "Rafael"
                    )
                    st.rerun()
                else:
                    st.error(response.json().get("detail", "No se pudo iniciar sesión"))
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown(
        """
        <div style="text-align: center; padding: 24px;">
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
    st.info("👈 Inicia sesión en el panel lateral para entrar al universo.")
    st.stop()


usuario_id = st.session_state.get("usuario_id")
headers = _headers()

# =========================
# BARRA LATERAL
# =========================
with st.sidebar:
    st.markdown(
        f"### 👤 Creador: **{st.session_state.get('nombre_usuario', 'Rafael')}**"
    )

    if st.button("🚪 Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.session_state["token"] = None
        st.session_state["usuario_id"] = None
        st.session_state["paso_onboarding"] = 1
        st.session_state["menu_activo"] = "🏠 Casa del Fundador"
        st.rerun()

    st.markdown("---")
    st.markdown("### 🗺️ Mundo")
    menu = st.radio(
        "Navegación",
        [
            "🏠 Casa del Fundador",
            "🌳 Bio-Estructura",
            "🎯 Misiones",
            "📖 Libro Vivo",
            "💬 XiXi",
            "🧾 ADN de Marca",
        ],
        index=[
            "🏠 Casa del Fundador",
            "🌳 Bio-Estructura",
            "🎯 Misiones",
            "📖 Libro Vivo",
            "💬 XiXi",
            "🧾 ADN de Marca",
        ].index(st.session_state.get("menu_activo", "🏠 Casa del Fundador")),
    )
    st.session_state["menu_activo"] = menu

    st.markdown("---")
    if st.button("🔥 Reiniciar Aventura desde Cero"):
        _safe_post_json(
            f"{API_URL}/usuarios/{usuario_id}/reset-base-cero",
            headers=headers,
            default={},
        )
        st.session_state["paso_onboarding"] = 1
        st.toast("🧹 Aventura reiniciada al inicio", icon="✨")
        st.rerun()

# =========================
# ONBOARDING
# =========================
if st.session_state["paso_onboarding"] < 5:
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

    elif st.session_state["paso_onboarding"] == 2:
        st.markdown(
            """
            <div class="hero-card" style="border-color: #38BDF8;">
                <h1 style="font-size: 70px; margin: 0;">👽</h1>
                <h1 style="color: #38BDF8; font-size: 42px;">2. BIENVENIDA DE XIXI</h1>
                <p style="font-size: 22px; color: #F3F4F6;">
                    ¡Hola! Soy <b>XiXi</b>, tu compañera de aventuras galácticas.
                    Estoy aquí para ayudarte a descubrir tu potencial y crear cosas increíbles.
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

# =========================
# DATOS DEL USUARIO
# =========================
user_data = _safe_get_json(f"{API_URL}/usuarios/", headers=headers, default=[])
if isinstance(user_data, list):
    user_data = next((u for u in user_data if u.get("id") == usuario_id), None)
else:
    user_data = None

pasaporte = user_data.get("pasaporte", {}) if user_data else {}
arbol = user_data.get("arbol", {}) if user_data else {}
libro = user_data.get("libro_vivo", {}) if user_data else {}

xp_actual = pasaporte.get("puntos_experiencia", 0)
nivel_actual = pasaporte.get("nivel_actual", (xp_actual // 100) + 1)
estado_arbol = arbol.get("estado_crecimiento", "semilla")

# =========================
# RENDER SEGÚN MÓDULO
# =========================
if menu == "🏠 Casa del Fundador":
    st.title("🏠 Casa del Fundador")
    st.write("Aquí comienza tu historia como creador.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="section-box">
                <h3>👤 Creador</h3>
                <p>{st.session_state.get("nombre_usuario", "Rafael")}</p>
                <p class="small-label">Avatar: {st.session_state["avatar_elegido"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="section-box">
                <h3>⭐ XP</h3>
                <p>{xp_actual}</p>
                <p class="small-label">Nivel actual: {nivel_actual}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="section-box">
                <h3>🌳 Bio-Estructura</h3>
                <p>{estado_arbol}</p>
                <p class="small-label">Energía: {arbol.get("energia_vital", 100)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("🧬 ADN de Marca")
    st.write(libro.get("resumen_adn", {}))

elif menu == "🌳 Bio-Estructura":
    st.title("🌳 Bio-Estructura")
    bio = _safe_get_json(
        f"{API_URL}/usuarios/{usuario_id}/bio-estructura", headers=headers, default={}
    )
    if bio:
        st.markdown(
            f"""
            <div class="section-box">
                <h2>{bio.get("fase_actual", "🌱 Semilla")}</h2>
                <p><b>Estado:</b> {bio.get("estado_crecimiento", "semilla")}</p>
                <p><b>Energía vital:</b> {bio.get("energia_vital", 100)}</p>
                <p><b>Nivel:</b> {bio.get("nivel", nivel_actual)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Actualizar Bio-Estructura"):
            st.rerun()

elif menu == "🎯 Misiones":
    st.title("🎯 Misiones")
    colg1, colg2 = st.columns([2, 1])

    with colg1:
        misiones = _safe_get_json(
            f"{API_URL}/usuarios/{usuario_id}/misiones/", headers=headers, default=[]
        )
        if isinstance(misiones, list) and misiones:
            for m in misiones:
                estado = m.get("estado", "pendiente")
                st.markdown(
                    f"""
                    <div class="section-box">
                        <h3>{m.get("titulo_mision", "Misión")}</h3>
                        <p>{m.get("descripcion", "")}</p>
                        <p><b>Estado:</b> {estado} | <b>Recompensa:</b> {m.get("recompensa_puntos", 0)} XP</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if estado == "pendiente":
                    if st.button(f"Completar {m.get('id')}"):
                        _safe_put_json(
                            f"{API_URL}/usuarios/{usuario_id}/misiones/{m['id']}/completar",
                            headers=headers,
                            default={},
                        )
                        st.success("Misión completada.")
                        st.rerun()
        else:
            st.info("Todavía no hay misiones. Genera la primera con XiXi.")

    with colg2:
        st.subheader("✨ Crear misión con XiXi")
        enfoque = st.selectbox(
            "Enfoque", ["emprendimiento", "creatividad", "finanzas", "marca"]
        )
        if st.button("Generar misión IA"):
            _safe_post_json(
                f"{API_URL}/usuarios/{usuario_id}/misiones/generar_ia?enfoque={enfoque}",
                headers=headers,
                default={},
            )
            st.success("Nueva misión creada.")
            st.rerun()

elif menu == "📖 Libro Vivo":
    st.title("📖 Libro Vivo")
    libro_estado = _safe_get_json(
        f"{API_URL}/usuarios/{usuario_id}/libro", headers=headers, default={}
    )
    st.markdown(
        f"""
        <div class="section-box">
            <h3>Capítulo actual: {libro_estado.get("capitulo_actual", 1)}</h3>
            <p>Paginas completadas: {libro_estado.get("paginas_completadas", 0)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("🧾 ADN de marca registrado")
    st.write(libro_estado.get("resumen_adn", {}))

    st.subheader("✍️ Actualizar ADN de marca")
    with st.form("form_adn"):
        nombre_empresa = st.text_input(
            "Nombre de empresa", value=st.session_state["nombre_empresa"]
        )
        eslogan = st.text_input("Eslogan", value=st.session_state["eslogan_empresa"])
        color_marca = st.text_input("Color de marca", value="Verde Bosque")
        enviar = st.form_submit_button("Guardar ADN")
        if enviar:
            _safe_put_json(
                f"{API_URL}/usuarios/{usuario_id}/libro/adn",
                payload={
                    "nombre_empresa": nombre_empresa,
                    "eslogan": eslogan,
                    "color_marca": color_marca,
                },
                headers=headers,
                default={},
            )
            st.session_state["nombre_empresa"] = nombre_empresa
            st.session_state["eslogan_empresa"] = eslogan
            st.success("ADN guardado.")
            st.rerun()

elif menu == "💬 XiXi":
    st.title("💬 XiXi")
    st.write("Habla con tu mentora de aprendizaje.")

    with st.form("form_xixi"):
        mensaje = st.text_area("Escribe tu mensaje para XiXi")
        rol_activo = st.selectbox(
            "Modo", ["emprendimiento", "creatividad", "finanzas", "marca"]
        )
        enviar = st.form_submit_button("Enviar")

        if enviar and mensaje.strip():
            resultado = _safe_post_json(
                f"{API_URL}/usuarios/{usuario_id}/interacciones/",
                payload={
                    "personaje": "xixi",
                    "mensaje_usuario": mensaje,
                    "respuesta_guia": "",
                    "rol_activo": rol_activo,
                },
                headers=headers,
                default={},
            )
            if resultado:
                st.success("XiXi respondió.")
                st.markdown(
                    f"""
                    <div class="section-box">
                        <h3>Respuesta</h3>
                        <p>{resultado.get("respuesta_guia", "")}</p>
                        <p class="small-label">Emoción: {resultado.get("emocion_detectada", "N/A")}</p>
                        <p class="small-label">XP: {resultado.get("xp_ganado", 0)} | Energía: {resultado.get("energia_ganada", 0)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

elif menu == "🧾 ADN de Marca":
    st.title("🧾 ADN de Marca")
    adn = libro.get("resumen_adn", {})
    if adn:
        st.json(adn)
    else:
        st.info("Todavía no has guardado el ADN de marca.")

st.markdown("---")
st.caption("Historias que Inspiran® · Versión de núcleo refactorizado")
