import streamlit as st
import requests

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
        # Crea el usuario por primera vez en la nube
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

    # Cargar datos consolidados
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

    st.markdown("---")

    # 1. VISOR GRÁFICO DEL ÁRBOL (MAPEO DINÁMICO DE 5 FASES)
    st.markdown("### 🌲 Bio-Estructura en Crecimiento")
    col_img, col_desc = st.columns([1, 4])

    estado_lower = estado_arbol.lower()

    if estado_lower == "semilla":
        grafico, desc = (
            "🌱",
            "Una pequeña bio-estructura descansa, llena de potencial cósmico.",
        )
    elif estado_lower == "brote":
        grafico, desc = (
            "🌿",
            "¡El tallo ha emergido! Tus emociones le otorgan fuerza vital.",
        )
    elif estado_lower == "arbol_joven":
        grafico, desc = (
            "🌳",
            "La estructura es firme. Las raíces procesan tu aprendizaje.",
        )
    elif estado_lower == "arbol_frondoso":
        grafico, desc = (
            "🌲",
            "Copa frondosa y raíces profundas. Refleja un alto grado de autoconocimiento.",
        )
    elif estado_lower in ["arbol_cosmico", "cosmico"]:
        grafico, desc = (
            "✨",
            "Manifestación de energía pura en plenitud. Has alcanzado la maestría del Libro Vivo.",
        )
    else:
        grafico, desc = "🌱", "Bio-estructura en fase inicial."

    with col_img:
        st.markdown(
            f"<h1 style='text-align: center; font-size: 80px; margin: 0;'>{grafico}</h1>",
            unsafe_allow_html=True,
        )
    with col_desc:
        st.info(
            f"**Fase Actual: {estado_arbol.replace('_', ' ').title()}**\n\n{desc}\n\n*Energía Vital Acumulada: {energia_vital} pts*"
        )

    st.markdown("---")

    # 2. INDICADORES VISUALES: ESCALERA DE NIVEL Y LIBRO CON HOJAS
    col1, col2 = st.columns(2)

    with col1:
        # Generación dinámica de la escalera según el nivel
        escalones = "🪜 " * nivel_actual
        st.markdown("### 🎓 Pasaporte de Nivel")
        st.metric(
            label="Ascenso de Nivel",
            value=f"Nivel {nivel_actual}",
            delta=f"{xp_actual} XP Totales",
        )
        st.write(f"**Escalera de Progreso:** {escalones} 🧗")

    with col2:
        # Generación dinámica de las hojas escritas del Libro Vivo
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
    # TAB 1: CHAT CON XIXI (CON AUTO-ESCRITURA EN LIBRO VIVO)
    # ---------------------------------------------------------
    with tab_chat:
        st.markdown("#### Frecuencia de Comunicación Alienígena Abierta")
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
                        # Rerun para refrescar el marcador de hojas del Libro Vivo automáticamente
                        st.rerun()
                    else:
                        st.error("Anomalía detectada. No se pudo enlazar con XiXi.")

    with tab_misiones:
        st.markdown("#### Desafíos de Sincronización")

        # Botón siempre visible para pruebas rápidas de XP
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
