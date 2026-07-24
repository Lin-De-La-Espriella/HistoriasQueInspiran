import streamlit as st
import requests
from streamlit_lottie import st_lottie

# Configuración de la página
st.set_page_config(page_title="Historias que Inspiran®", page_icon="🌱", layout="wide")

# Dirección base del Backend FastAPI
API_URL = "https://historias-que-inspiran-api.onrender.com"

# Credenciales de Autologin para Desarrollo
DEV_EMAIL = "lindley@historias.com"
DEV_PASS = "superPassword123"

# Inicialización de estados de sesión
if "token" not in st.session_state:
    st.session_state.token = None
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# FUNCIONES AUXILIARES GLOBALES
# ---------------------------------------------------------
@st.cache_data
def cargar_lottie(url: str):
    """Carga y almacena en caché animaciones Lottie desde una URL."""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def autenticar_usuario(email, password):
    """Función auxiliar para solicitar el token e identificar al usuario."""
    response = requests.post(
        f"{API_URL}/token", data={"username": email, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        st.session_state.token = data["access_token"]

        res_users = requests.get(f"{API_URL}/usuarios/")
        if res_users.status_code == 200:
            usuarios = res_users.json()
            user_obj = next((u for u in usuarios if u["email"] == email), None)
            if user_obj:
                st.session_state.usuario_id = user_obj["id"]
        return True
    return False


# Autologin automático y Control de Render
if not st.session_state.token:
    try:
        if autenticar_usuario(DEV_EMAIL, DEV_PASS):
            st.rerun()
    except requests.exceptions.ConnectionError:
        st.error(
            "⏳ El cerebro en Render se está despertando (Cold Start). Espera 30 segundos y recarga la página."
        )
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        st.stop()

# Estilos CSS Personalizados para la Ventana Flotante de XiXi
st.markdown(
    """
    <style>
    .xixi-floating-badge {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #1f2937;
        color: #00ffcc;
        padding: 12px 20px;
        border-radius: 30px;
        box-shadow: 0px 4px 15px rgba(0, 255, 204, 0.3);
        border: 2px solid #00ffcc;
        font-weight: bold;
        z-index: 999999;
        cursor: pointer;
    }
    </style>
    <div class="xixi-floating-badge">
        👽 XiXi Órbita Activa | Transmisión En Vivo
    </div>
""",
    unsafe_allow_html=True,
)

st.title("🌱 Historias que Inspiran®")
st.subheader("Plataforma EdTech Gamificada")

# Manejador del Estado Vacío de la Base de Datos
if not st.session_state.token:
    st.warning(
        "⚠️ Base de datos en la nube conectada, pero se encuentra en blanco. No existe el usuario maestro."
    )
    if st.button("🚀 Inyectar Usuario de Desarrollo en Supabase"):
        payload = {
            "email": DEV_EMAIL,
            "nombre": "Administrador (Nube)",
            "password": DEV_PASS,
        }
        res_crear = requests.post(f"{API_URL}/usuarios/", json=payload)

        if res_crear.status_code in [200, 201]:
            st.success("¡Estructura base inicializada! Reiniciando interfaz...")
            st.rerun()
        else:
            st.error(f"Error de inyección: {res_crear.text}")
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    usuario_id = st.session_state.usuario_id or 1

    st.sidebar.success("🔑 Sesión Autenticada (DEV)")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.token = None
        st.session_state.usuario_id = None
        st.session_state.messages = []
        st.rerun()

    # ---------------------------------------------------------
    # BARRA LATERAL (SIDEBAR) - PANEL DE CONTROL Y DEV TOOLS
    # ---------------------------------------------------------
    with st.sidebar:
        st.markdown("### 👤 Sesión de Usuario")
        st.info(f"**ID:** `{usuario_id}`\n\n**Conexión:** `Supabase Realtime`")

        if st.button("🚪 Cerrar Sesión"):
            st.session_state.pop("usuario_id", None)
            st.rerun()

        st.markdown("---")
        st.markdown("### 🧪 Inspector de Bio-Estructuras (DEV)")

        opciones_fases = [
            ("semilla", "1. Semilla"),
            ("brote_menor", "2. Brote Menor"),
            ("brote_explorador", "3. Brote Explorador"),
            ("arbol_joven_enraizado", "4. Árbol Joven Enraizado"),
            ("arbol_joven_creativo", "5. Árbol Joven Creativo"),
            ("arbol_joven_empatico", "6. Árbol Joven Empático"),
            ("arbol_frondoso_lider", "7. Árbol Frondoso Líder"),
            ("arbol_frondoso_visionario", "8. Árbol Frondoso Visionario"),
            ("arbol_frondoso_sabio", "9. Árbol Frondoso Sabio"),
            ("arbol_cosmico", "10. Árbol Cósmico"),
        ]

        fase_seleccionada = st.selectbox(
            "Simular Vista de Fase:",
            options=[op[0] for op in opciones_fases],
            format_func=lambda x: dict(opciones_fases).get(x, x),
            key="select_fase_dev",
        )

        if st.button("👁️ Simular Fase en Pantalla"):
            st.session_state["estado_arbol_override"] = fase_seleccionada
            st.rerun()

        if "estado_arbol_override" in st.session_state:
            if st.button("🔄 Restablecer a Datos Reales"):
                del st.session_state["estado_arbol_override"]
                st.rerun()

    # ---------------------------------------------------------
    # OBTENCIÓN DE DATOS REALES DE LA BASE DE DATOS
    # ---------------------------------------------------------
    res_users = requests.get(f"{API_URL}/usuarios/", headers=headers)
    user_data = None
    if res_users.status_code == 200:
        user_data = next((u for u in res_users.json() if u["id"] == usuario_id), None)

    pasaporte = user_data.get("pasaporte", {}) if user_data else {}
    arbol = user_data.get("arbol", {}) if user_data else {}
    libro = user_data.get("libro_vivo", {}) if user_data else {}

    nivel_actual = pasaporte.get("nivel_actual", 1)
    xp_actual = pasaporte.get("puntos_experiencia", 0)
    estado_arbol = arbol.get("estado_crecimiento", "semilla")
    energia_vital = arbol.get("energia_vital", 100)

    capitulo_actual = libro.get("capitulo_actual", 1)
    paginas_completadas = libro.get("paginas_completadas", 1)

    # Prioridad de simulación DEV
    if "estado_arbol_override" in st.session_state:
        estado_arbol = st.session_state["estado_arbol_override"]

    st.markdown("---")

    # ---------------------------------------------------------
    # 1. VISOR GRÁFICO DEL ÁRBOL (ANIMACIONES LOTTIE GARANTIZADAS)
    # ---------------------------------------------------------
    st.markdown("### 🌲 Bio-Estructura en Crecimiento")
    col_img, col_desc = st.columns([1, 4])

    estado_lower = estado_arbol.lower()

    # Mapeo con enlaces activos y probados en lottie.host
    mapeo_bio = {
        "semilla": (
            "https://lottie.host/8157854c-18e2-4553-af24-9adff0a34361/mAnIMaTIOn.json",
            "1. Semilla (El Inicio de Todo)",
            "Despertar la curiosidad y la seguridad básica.",
            "Abre la mente al aprendizaje y la exploración.",
            "Comienzo a reconocer mi lugar en el mundo.",
            "Conecta con su esencia y propósito personal.",
            "Descubre quién soy y qué me hace único.",
        ),
        "brote_menor": (
            "https://lottie.host/5b2e5a1a-41f2-4977-8c38-8e6822c60e3a/f290L2R8Q1.json",
            "2. Brote Menor (Mis Primeros Pasos)",
            "Desarrolla la confianza y la alegría de aprender.",
            "Fortalece la atención y la memoria.",
            "Inicia la empatía y la colaboración.",
            "Descubre la magia de la vida y la gratitud.",
            "Exploro, juego y aprendo a conocer mi mundo.",
        ),
        "brote_explorador": (
            "https://lottie.host/82d9212c-5b23-45a8-9d82-8418ffed43b2/9ZpZJzW3O0.json",
            "3. Brote Explorador (Descubro y Me Pregunto)",
            "Aumenta la autoestima y la curiosidad sana.",
            "Desarrolla el pensamiento lógico y la creatividad.",
            "Fortalece la comunicación y el trabajo en equipo.",
            "Se conecta con su intuición y su voz interior.",
            "Hago preguntas, busco respuestas y entiendo más.",
        ),
        "arbol_joven_enraizado": (
            "https://lottie.host/a6133a88-82bc-4402-9a00-1c94411fb2d0/9ZpZJzW3O0.json",
            "4. Árbol Joven Enraizado (Construyo Mis Bases)",
            "Genera estabilidad emocional y autodisciplina.",
            "Organiza ideas y establece metas.",
            "Construye relaciones de confianza.",
            "Fortalece su identidad y sus principios.",
            "Formo hábitos, valores y una base sólida.",
        ),
        "arbol_joven_creativo": (
            "https://lottie.host/82d9212c-5b23-45a8-9d82-8418ffed43b2/9ZpZJzW3O0.json",
            "5. Árbol Joven Creativo (Creo y Transformo)",
            "Potencia la motivación y la expresión personal.",
            "Desarrolla la creatividad y la resolución de problemas.",
            "Inspira y motiva a otros con su originalidad.",
            "Descubre su propósito y talentos únicos.",
            "Imagino, creo y doy vida a mis ideas.",
        ),
        "arbol_joven_empatico": (
            "https://lottie.host/5b2e5a1a-41f2-4977-8c38-8e6822c60e3a/f290L2R8Q1.json",
            "6. Árbol Joven Empático (Entiendo y Me Conecto)",
            "Profundiza la empatía y la inteligencia emocional.",
            "Amplía la visión y el pensamiento crítico.",
            "Fortalece la empatía, el respeto y la inclusión.",
            "Comprende la unidad y la interconexión de la vida.",
            "Me pongo en el lugar del otro y construyo puentes.",
        ),
        "arbol_frondoso_lider": (
            "https://lottie.host/a6133a88-82bc-4402-9a00-1c94411fb2d0/9ZpZJzW3O0.json",
            "7. Árbol Frondoso Líder (Guío e Inspiro)",
            "Fortalece la confianza y la madurez emocional.",
            "Toma decisiones con sabiduría y responsabilidad.",
            "Influye positivamente en su comunidad.",
            "Usa su luz para servir y transformar entornos.",
            "Lidero con el ejemplo y dejo huella positiva.",
        ),
        "arbol_frondoso_visionario": (
            "https://lottie.host/8157854c-18e2-4553-af24-9adff0a34361/mAnIMaTIOn.json",
            "8. Árbol Frondoso Visionario (Sueño en Grande)",
            "Desarrolla resiliencia y determinación.",
            "Piensa en grande y anticipa soluciones innovadoras.",
            "Crea proyectos que impactan a muchos.",
            "Confía en su propósito y en el camino del alma.",
            "Tengo visión, planifico y transformo sueños en realidades.",
        ),
        "arbol_frondoso_sabio": (
            "https://lottie.host/82d9212c-5b23-45a8-9d82-8418ffed43b2/9ZpZJzW3O0.json",
            "9. Árbol Frondoso Sabio (Comparto Mi Sabiduría)",
            "Refuerza la gratitud y la generosidad.",
            "Integra conocimiento y experiencia para guiar.",
            "Forma líderes y deja un impacto duradero.",
            "Vive su propósito y deja huella en la historia.",
            "Enseño, acompaño y dejo legado a otros.",
        ),
        "arbol_cosmico": (
            "https://lottie.host/a6133a88-82bc-4402-9a00-1c94411fb2d0/9ZpZJzW3O0.json",
            "10. Árbol Cósmico (Unido al Universo)",
            "Alcanza la paz interior y plenitud del alma.",
            "Trasciende límites y comprende la verdad universal.",
            "Es faro de luz e inspiración para la humanidad.",
            "Conecta con la energía divina y el todo.",
            "Estoy en paz, en unidad y expando mi luz al universo.",
        ),
    }

    url_anim, titulo_fase, emo, men, soc, esp, frase = mapeo_bio.get(
        estado_lower,
        (
            "https://lottie.host/8157854c-18e2-4553-af24-9adff0a34361/mAnIMaTIOn.json",
            "1. Semilla (El Inicio de Todo)",
            "Despertar la curiosidad y la seguridad básica.",
            "Abre la mente al aprendizaje y la exploración.",
            "Comienzo a reconocer mi lugar en el mundo.",
            "Conecta con su esencia y propósito personal.",
            "Descubre quién soy y qué me hace único.",
        ),
    )

    # Cargar animación Lottie
    animacion_json = cargar_lottie(url_anim)

    # COLUMNA IZQUIERDA: RENDERIZADO DINÁMICO
    with col_img:
        if animacion_json:
            # El key incluye el nombre de la fase para forzar el refresco visual en Streamlit
            st_lottie(animacion_json, height=140, key=f"lottie_view_{estado_lower}")
        else:
            # Fallback visual usando el ícono emoji correspondiente si falla la red
            emojis_fase = {
                "semilla": "🟡",
                "brote_menor": "🌱",
                "brote_explorador": "🍃",
                "arbol_joven_enraizado": "🪵",
                "arbol_joven_creativo": "🌳",
                "arbol_joven_empatico": "💜",
                "arbol_frondoso_lider": "🌲",
                "arbol_frondoso_visionario": "🍂",
                "arbol_frondoso_sabio": "🌸",
                "arbol_cosmico": "✨",
            }
            icono_fallback = emojis_fase.get(estado_lower, "🌱")
            st.markdown(
                f"<h1 style='text-align: center; font-size: 75px; margin: 0;'>{icono_fallback}</h1>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<p style='text-align: center; font-size: 14px; color: #4CAF50; font-weight: bold; margin-top: 5px;'>"
            f"⚡ Energía Vital<br><span style='font-size: 18px;'>{energia_vital} pts</span></p>",
            unsafe_allow_html=True,
        )

    # COLUMNA DERECHA: FRANJA AZUL MULTIDIMENSIONAL
    with col_desc:
        contenido_tarjeta = f"""
        ### 📍 **Fase Actual: {titulo_fase}**
        *{frase}*

        ---
        * **❤️ Emocional:** {emo}
        * **🧠 Mental:** {men}
        * **👥 Social:** {soc}
        * **✨ Espiritual:** {esp}
        """
        st.info(contenido_tarjeta)

    st.markdown("---")

    # ---------------------------------------------------------
    # 2. INDICADORES VISUALES: ESCALERA DE NIVEL Y LIBRO CON HOJAS
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        escalones = "🪜 " * nivel_actual
        st.markdown("### 🎓 Pasaporte de Nivel")
        st.metric(
            label="Ascenso de Nivel",
            value=f"Nivel {nivel_actual}",
            delta=f"{xp_actual} XP Totales",
        )
        st.write(f"**Escalera de Progreso:** {escalones} 🧗")

    with col2:
        total_paginas = 5
        hojas_escritas = "📄 " * paginas_completadas
        hojas_vacias = "⬜ " * (total_paginas - paginas_completadas)

        st.markdown("### 📖 Libro Vivo")
        st.metric(
            label="Progreso de Historia",
            value=f"Capítulo {capitulo_actual}",
            delta=f"{paginas_completadas}/{total_paginas} Hojas Llenas",
        )
        st.write(f"**Páginas Escribiéndose:** {hojas_escritas}{hojas_vacias}")

    st.markdown("---")

    # PESTAÑAS DE INTERACCIÓN
    tab_chat, tab_misiones = st.tabs(
        ["👽 Contactar a XiXi", "🎯 Misiones de Evolución"]
    )

    # ---------------------------------------------------------
    # TAB 1: CHAT CON XIXI
    # ---------------------------------------------------------
    with tab_chat:
        st.markdown("#### Frecuencia de Comunicación Alienígena Abierta")
        st.caption("XiXi está en línea decodificando tu proceso en tiempo real.")
        st.markdown("---")

        avatar_dict = {"user": "🧑‍🎓", "assistant": "👽"}

        for message in st.session_state.messages:
            with st.chat_message(
                message["role"], avatar=avatar_dict.get(message["role"])
            ):
                st.markdown(message["content"])

        if prompt := st.chat_input("Transmite tu mensaje a XiXi..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="👽"):
                with st.spinner(
                    "XiXi está decodificando tus frecuencias emocionales..."
                ):
                    payload = {
                        "personaje": "xixi",
                        "mensaje_usuario": prompt,
                        "respuesta_guia": "",
                    }
                    res_chat = requests.post(
                        f"{API_URL}/usuarios/{usuario_id}/interacciones/",
                        json=payload,
                        headers=headers,
                    )

                    if res_chat.status_code == 201:
                        respuesta = res_chat.json()["respuesta_guia"]
                        st.markdown(respuesta)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": respuesta}
                        )
                        st.rerun()
                    else:
                        st.error("Anomalía detectada. No se pudo enlazar con XiXi.")

    # ---------------------------------------------------------
    # TAB 2: MISIONES
    # ---------------------------------------------------------
    with tab_misiones:
        st.markdown("#### Desafíos de Sincronización")

        if st.button("⚡ Generar Misión de Prueba (+50 XP)"):
            mision_payload = {
                "titulo_mision": f"Reflexión Emocional #{st.session_state.get('mision_count', 1)}",
                "recompensa_puntos": 50,
            }
            res_gen = requests.post(
                f"{API_URL}/usuarios/{usuario_id}/misiones/",
                json=mision_payload,
                headers=headers,
            )
            if res_gen.status_code in [200, 201]:
                st.session_state["mision_count"] = (
                    st.session_state.get("mision_count", 1) + 1
                )
                st.rerun()

        st.markdown("---")

        res_misiones = requests.get(
            f"{API_URL}/usuarios/{usuario_id}/misiones/", headers=headers
        )

        if res_misiones.status_code == 200:
            misiones = res_misiones.json()
            if not misiones:
                st.info(
                    "No tienes misiones activas. Usa el botón de arriba para generar una."
                )
            else:
                for m in misiones:
                    col_m1, col_m2 = st.columns([3, 1])
                    with col_m1:
                        st.write(
                            f"**{m['titulo_mision']}** | Recompensa: `+{m['recompensa_puntos']} XP`"
                        )
                    with col_m2:
                        if m["estado"] == "completada":
                            st.success("✅ Sincronizada")
                        else:
                            if st.button(
                                f"Procesar #{m['id']}", key=f"mision_{m['id']}"
                            ):
                                res_complete = requests.put(
                                    f"{API_URL}/usuarios/{usuario_id}/misiones/{m['id']}/completar",
                                    headers=headers,
                                )
                                if res_complete.status_code == 200:
                                    st.success("¡Desafío completado!")
                                    st.rerun()
                                else:
                                    st.error("Fallo de procesamiento.")
