import streamlit as st
import requests

# Configuración de la página
st.set_page_config(page_title="Historias que Inspiran®", page_icon="🌱", layout="wide")

# Dirección base del Backend FastAPI
API_URL = "http://127.0.0.1:8000"

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


# Autologin automático
if not st.session_state.token:
    try:
        if autenticar_usuario(DEV_EMAIL, DEV_PASS):
            st.rerun()
    except Exception:
        pass

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

if not st.session_state.token:
    st.warning("Accediendo al entorno de desarrollo...")
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

    # 1. VISOR GRÁFICO DEL ÁRBOL
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
    else:
        grafico, desc = "✨", "Manifestación de energía pura en desarrollo."

    with col_img:
        st.markdown(
            f"<h1 style='text-align: center; font-size: 80px; margin: 0;'>{grafico}</h1>",
            unsafe_allow_html=True,
        )
    with col_desc:
        st.info(
            f"**Fase Actual: {estado_arbol.capitalize()}**\n\n{desc}\n\n*Energía Vital Acumulada: {energia_vital}*"
        )

    st.markdown("---")

    # 2. INDICADORES VISUALES: ESCALERA DE NIVEL Y LIBRO CON HOJAS
    col1, col2 = st.columns(2)

    with col1:
        # Generación dinámica de la escalera según el nivel
        escalones = "🪜 " * nivel_actual
        st.markdown(f"### 🎓 Pasaporte de Nivel")
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

        st.markdown(f"### 📖 Libro Vivo")
        st.metric(
            label="Progreso de Historia",
            value=f"Capítulo {capitulo_actual}",
            delta=f"{paginas_completadas}/{total_paginas} Hojas Llenas",
        )
        st.write(f"**Páginas Escribiéndose:** {hojas_escritas}{hojas_vacias}")

        # Botón para simular el registro de un aprendizaje con XiXi
        if st.button("✍️ Registrar Reflexión (+1 Hoja)"):
            res_aviso = requests.put(
                f"{API_URL}/usuarios/{usuario_id}/libro/avanzar-pagina", headers=headers
            )
            if res_aviso.status_code == 200:
                st.success("¡Reflexión guardada en el Libro Vivo!")
                st.rerun()
            else:
                st.error("No se pudo registrar la página.")

    st.markdown("---")

    # PESTAÑAS DE INTERACCIÓN
    tab_chat, tab_misiones = st.tabs(
        ["👽 Contactar a XiXi", "🎯 Misiones de Evolución"]
    )

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
                    else:
                        st.error("Anomalía detectada. No se pudo enlazar con XiXi.")

    with tab_misiones:
        st.markdown("#### Desafíos de Sincronización")

        res_misiones = requests.get(
            f"{API_URL}/usuarios/{usuario_id}/misiones/", headers=headers
        )

        if res_misiones.status_code == 200 and len(res_misiones.json()) == 0:
            st.info("Sin anomalías pendientes. ¡Inicia un ciclo de prueba!")
            if st.button("➕ Generar Misión: 'Reflexión Emocional Diaria' (+50 XP)"):
                mision_payload = {
                    "titulo_mision": "Reflexión Emocional Diaria: Identifica tus emociones hoy",
                    "recompensa_puntos": 50,
                }
                requests.post(
                    f"{API_URL}/usuarios/{usuario_id}/misiones/",
                    json=mision_payload,
                    headers=headers,
                )
                st.rerun()

        elif res_misiones.status_code == 200:
            misiones = res_misiones.json()
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
                        if st.button(f"Procesar #{m['id']}", key=f"mision_{m['id']}"):
                            res_complete = requests.put(
                                f"{API_URL}/usuarios/{usuario_id}/misiones/{m['id']}/completar",
                                headers=headers,
                            )
                            if res_complete.status_code == 200:
                                st.success("¡Desafío completado!")
                                st.rerun()
                            else:
                                st.error("Fallo de procesamiento.")
