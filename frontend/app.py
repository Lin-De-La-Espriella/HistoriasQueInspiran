import json
import os
import requests
import streamlit as st
import io
from fpdf import FPDF
from streamlit_lottie import st_lottie

# Configuración de la página
st.set_page_config(page_title="Historias que Inspiran®", page_icon="🌱", layout="wide")

# ---------------------------------------------------------
# 🚀 BYPASS DE DESARROLLO: AUTO-LOGIN ACTIVO
# ---------------------------------------------------------
# Este bloque inyecta las credenciales de sesión automáticamente.
# Comenta o elimina este bloque antes del despliegue final a producción.

import requests
import streamlit as st

# ==========================================
# 📍 ENRUTAMIENTO DE ENTORNO E INICIALIZACIÓN
# ==========================================
API_URL = "https://historias-que-inspiran-api.onrender.com"

# Credenciales de acceso rápido para pruebas
DEV_EMAIL = "lindley@historias.com"
DEV_PASS = "superPassword123"

# 1. Inicialización estructurada de estados de sesión
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None
if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---------------------------------------------------------
# 🔒 SISTEMA DE AUTENTICACIÓN JWT SEGURO (PRODUCCIÓN & MULTI-PERFIL)
# ---------------------------------------------------------
if not st.session_state.get("autenticado", False):
    st.sidebar.markdown("### 🔐 Acceso a la Plataforma")

    # 1. Enrutamiento Visual: Pestañas de Login y Registro
    tab_login, tab_registro = st.sidebar.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])

    # --- PESTAÑA 1: INICIO DE SESIÓN ---
    with tab_login:
        # Formulario con valores por defecto para agilizar el flujo de pruebas
        email_input = st.text_input(
            "Correo Electrónico", value=DEV_EMAIL, key="login_email"
        )
        password_input = st.text_input(
            "Contraseña", type="password", value=DEV_PASS, key="login_pass"
        )

        if st.button("🔑 Ingresar", key="btn_login"):
            if not email_input or not password_input:
                st.warning("Por favor ingresa credenciales válidas.")
            else:
                try:
                    # Petición HTTP al endpoint de seguridad
                    response = requests.post(
                        f"{API_URL}/auth/login",
                        json={"email": email_input, "password": password_input},
                    )

                    if response.status_code == 200:
                        data_token = response.json()

                        # 2. Asignación de credenciales seguras (Dinámico)
                        st.session_state["token"] = data_token.get("access_token")
                        st.session_state["autenticado"] = True

                        # Mapeo dinámico desde la DB con fallback a entorno local
                        st.session_state["usuario_id"] = data_token.get("usuario_id", 1)
                        st.session_state["nombre_usuario"] = data_token.get(
                            "nombre", "Lindley"
                        )

                        # 3. Inicialización Base Cero en UI (Mejora Continua: A futuro esto vendrá de la DB)
                        st.session_state["nivel"] = 1
                        st.session_state["xp_totales"] = 0
                        st.session_state["fase_arbol"] = "1. Semilla"
                        st.session_state["mision_count"] = 1
                        st.session_state["capitulo_actual"] = 1
                        st.session_state["paginas_completadas"] = 0

                        st.success("¡Sesión iniciada con éxito!")
                        st.rerun()
                    else:
                        st.error(
                            "Credenciales incorrectas. Verifica tu acceso en la base de datos."
                        )
                except Exception as e:
                    st.error(f"Error crítico de conexión: {e}")

    # --- PESTAÑA 2: REGISTRO DE NUEVO ESTUDIANTE ---
    with tab_registro:
        nuevo_nombre = st.text_input("Nombre Completo", key="reg_nombre")
        nuevo_email = st.text_input("Correo Electrónico", key="reg_email")
        nueva_pass = st.text_input("Contraseña", type="password", key="reg_pass")

        if st.button("📝 Registrarme Base Cero", key="btn_registro"):
            if not nuevo_nombre or not nuevo_email or not nueva_pass:
                st.warning("Completa todos los campos para registrarte.")
            else:
                payload = {
                    "nombre": nuevo_nombre,
                    "email": nuevo_email,
                    "password": nueva_pass,
                    "rol": "estudiante",
                }
                try:
                    res_reg = requests.post(f"{API_URL}/usuarios/", json=payload)
                    if res_reg.status_code == 201:
                        st.success(
                            "¡Cuenta creada exitosamente! Ahora ve a la pestaña Iniciar Sesión."
                        )
                    else:
                        st.error(
                            "Error en el registro. El correo podría ya estar en uso."
                        )
                except Exception as e:
                    st.error(f"Error al conectar con el servidor: {e}")

    # 4. Bloqueo de renderizado: Evita que cargue la app si no hay sesión
    st.warning(
        "⚠️ Debes iniciar sesión en la barra lateral para acceder al motor gamificado."
    )
    st.stop()

# ==========================================
# 🛡️ CABECERAS SEGURAS GLOBALES
# ==========================================
# Este diccionario se usará en todas las llamadas (requests) al backend a partir de aquí
headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
st.sidebar.success("✅ Conexión Segura Activa (JWT)")
st.sidebar.markdown("---")


# ---------------------------------------------------------
# FUNCIONES AUXILIARES GLOBALES
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def cargar_lottie_local(filepath: str):
    """Carga una animación Lottie directamente desde un archivo físico local."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def autenticar_usuario(email, password):
    """Función auxiliar para solicitar el token e identificar al usuario vía JSON puro."""
    try:
        # Limpieza estricta de espacios
        email_limpio = email.strip()
        pass_limpio = password.strip()

        # Uso del nuevo endpoint /auth/login nativo JSON
        payload = {"email": email_limpio, "password": pass_limpio}
        response = requests.post(f"{API_URL}/auth/login", json=payload)

        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]

            res_users = requests.get(f"{API_URL}/usuarios/")
            if res_users.status_code == 200:
                usuarios = res_users.json()
                user_obj = next(
                    (u for u in usuarios if u["email"] == email_limpio), None
                )
                if user_obj:
                    st.session_state.usuario_id = user_obj["id"]
            return True
        else:
            # Visión de Rayos X activada: Imprimimos el error exacto si falla
            st.error(f"Fallo en el Login ({response.status_code}): {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        st.error("⏳ No se pudo conectar con el servidor (Render / Localhost).")
        return False


# Estilos CSS Personalizados
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

# =========================================================
# RUTEO PRINCIPAL: NO AUTENTICADO vs AUTENTICADO
# =========================================================
if not st.session_state.token:
    # --- MENÚ LATERAL PARA VISITANTES ---
    with st.sidebar:
        st.title("Navegación")
        modo = st.radio(
            "Selecciona una opción:",
            ["Iniciar Sesión", "Registrarse", "Estado del Sistema (DEV)"],
        )

    # --- PANTALLA DE INICIO DE SESIÓN ---
    if modo == "Iniciar Sesión":
        st.markdown("### 🔑 Acceso a la Plataforma")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            if autenticar_usuario(email, password):
                st.success("¡Acceso concedido! Sincronizando biometría...")
                st.rerun()
            # El "else" con error genérico se elimina porque autenticar_usuario ya imprime el error exacto.

    # --- PANTALLA DE REGISTRO ---
    elif modo == "Registrarse":
        st.markdown("### 📝 Crear Nueva Cuenta")

        with st.form("form_registro", clear_on_submit=False):
            nuevo_nombre = st.text_input("Nombre Completo", key="reg_nombre")
            nuevo_email = st.text_input("Correo Electrónico", key="reg_email")
            nuevo_password = st.text_input(
                "Contraseña", type="password", key="reg_pass"
            )

            btn_registrar = st.form_submit_button("Crear Cuenta")

        if btn_registrar:
            if nuevo_nombre.strip() and nuevo_email.strip() and nuevo_password.strip():
                payload = {
                    "nombre": nuevo_nombre.strip(),
                    "email": nuevo_email.strip(),
                    "password": nuevo_password.strip(),
                }
                try:
                    res_crear = requests.post(f"{API_URL}/usuarios/", json=payload)
                    if res_crear.status_code in [200, 201]:
                        st.success(
                            "¡Usuario creado exitosamente! Sincronizando acceso..."
                        )
                        if autenticar_usuario(
                            nuevo_email.strip(), nuevo_password.strip()
                        ):
                            st.rerun()
                    else:
                        st.error(f"Error al registrar: {res_crear.text}")
                except Exception as e:
                    st.error(f"Fallo de conexión: {e}")
            else:
                st.warning("Por favor completa todos los campos obligatorios.")

    # --- PANTALLA DE INYECCIÓN DE DATOS (Mantenimiento) ---
    elif modo == "Estado del Sistema (DEV)":
        st.warning("⚠️ Módulo de diagnóstico de Base de Datos")
        st.info(
            "Utiliza esta opción únicamente si la base de datos de Render/Supabase"
            " está completamente en blanco."
        )

        if st.button("🚀 Inyectar Usuario de Desarrollo en Supabase"):
            payload = {
                "email": DEV_EMAIL,
                "nombre": "Administrador (Nube)",
                "password": DEV_PASS,
            }
            try:
                res_crear = requests.post(f"{API_URL}/usuarios/", json=payload)
                if res_crear.status_code in [200, 201]:
                    st.success(
                        "¡Estructura base inicializada correctamente! Ve a Iniciar"
                        " Sesión."
                    )
                else:
                    st.error(f"Error de inyección: {res_crear.text}")
            except Exception as e:
                st.error(f"Fallo crítico de conexión: {e}")

else:
    # =========================================================
    # PANEL DE CONTROL (USUARIO AUTENTICADO)
    # =========================================================
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    usuario_id = st.session_state.usuario_id or 1

    # --- BARRA LATERAL DEL SISTEMA ---
    with st.sidebar:
        st.success("🔑 Sesión Autenticada")
        st.markdown("### 👤 Sesión de Usuario")
        st.info(f"**ID:** `{usuario_id}`\n\n**Conexión:** `Render Nube`")

        if st.button("🚪 Cerrar Sesión"):
            st.session_state.token = None
            st.session_state.usuario_id = None
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.markdown("### 🧹 Mantenimiento de Datos (DEV)")
        if st.button("🔥 Reiniciar Usuario a Base Cero (0 XP)"):
            res_reset = requests.post(
                f"{API_URL}/usuarios/{usuario_id}/reset-base-cero", headers=headers
            )
            if res_reset.status_code == 200:
                st.toast("🧹 Usuario reiniciado a Nivel 1 (0 XP)", icon="✨")
                st.rerun()
            else:
                st.error("No se pudo procesar el reset.")

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

    # --- OBTENCIÓN DE DATOS REALES ---
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

    if "estado_arbol_override" in st.session_state:
        estado_arbol = st.session_state["estado_arbol_override"]

    st.markdown("---")

    # --- 1. VISOR GRÁFICO DEL ÁRBOL ---
    st.markdown("### 🌲 Bio-Estructura en Crecimiento")
    col_img, col_desc = st.columns([1, 4])

    estado_limpio = estado_arbol.strip().lower()

    mapeo_bio = {
        "semilla": (
            "frontend/assets/semilla.json",
            "1. Semilla (El Inicio de Todo)",
            "Despertar la curiosidad y la seguridad básica.",
            "Abre la mente al aprendizaje y la exploración.",
            "Comienzo a reconocer mi lugar en el mundo.",
            "Conecta con su esencia y propósito personal.",
            "Descubre quién soy y qué me hace único.",
        ),
        "brote_menor": (
            "frontend/assets/brote_menor.json",
            "2. Brote Menor (Mis Primeros Pasos)",
            "Desarrolla la confianza y la alegría de aprender.",
            "Fortalece la atención y la memoria.",
            "Inicia la empatía y la colaboración.",
            "Descubre la magia de la vida y la gratitud.",
            "Exploro, juego y aprendo a conocer mi mundo.",
        ),
        "brote_explorador": (
            "frontend/assets/brote_explorador.json",
            "3. Brote Explorador (Descubro y Me Pregunto)",
            "Aumenta la autoestima y la curiosidad sana.",
            "Desarrolla el pensamiento lógico y la creatividad.",
            "Fortalece la comunicación y el trabajo en equipo.",
            "Se conecta con su intuición y su voz interior.",
            "Hago preguntas, busco respuestas y entiendo más.",
        ),
        "arbol_joven_enraizado": (
            "frontend/assets/arbol_joven_enraizado.json",
            "4. Árbol Joven Enraizado (Construyo Mis Bases)",
            "Genera estabilidad emocional y autodisciplina.",
            "Organiza ideas y establece metas.",
            "Construye relaciones de confianza.",
            "Fortalece su identidad y sus principios.",
            "Formo hábitos, valores y una base sólida.",
        ),
        "arbol_joven_creativo": (
            "frontend/assets/arbol_joven_creativo.json",
            "5. Árbol Joven Creativo (Creo y Transformo)",
            "Potencia la motivación y la expression personal.",
            "Desarrolla la creatividad y la resolución de problemas.",
            "Inspira y motiva a otros con su originalidad.",
            "Descubre su propósito y talentos únicos.",
            "Imagino, creo y doy vida a mis ideas.",
        ),
        "arbol_joven_empatico": (
            "frontend/assets/arbol_joven_empatico.json",
            "6. Árbol Joven Empático (Entiendo y Me Conecto)",
            "Profundiza la empatía y la inteligencia emocional.",
            "Amplía la visión y el pensamiento crítico.",
            "Fortalece la empatía, el respeto y la inclusión.",
            "Comprende la unidad y la interconexión de la vida.",
            "Me pongo en el lugar del otro y construyo puentes.",
        ),
        "arbol_frondoso_lider": (
            "frontend/assets/arbol_frondoso_lider.json",
            "7. Árbol Frondoso Líder (Guío e Inspiro)",
            "Fortalece la confianza y la madurez emocional.",
            "Toma decisiones con sabiduría y responsabilidad.",
            "Influye positivamente en su comunidad.",
            "Usa su luz para servir y transformo entornos.",
            "Lidero con el ejemplo y dejo huella positiva.",
        ),
        "arbol_frondoso_visionario": (
            "frontend/assets/arbol_frondoso_visionario.json",
            "8. Árbol Frondoso Visionario (Sueño en Grande)",
            "Desarrolla resiliencia y determinación.",
            "Piensa en grande y anticipa soluciones innovadoras.",
            "Crea proyectos que impactan a muchos.",
            "Confía en su propósito y en el camino del alma.",
            "Tengo visión, planifico y transformo sueños en realidades.",
        ),
        "arbol_frondoso_sabio": (
            "frontend/assets/arbol_frondoso_sabio.json",
            "9. Árbol Frondoso Sabio (Comparto Mi Sabiduría)",
            "Refuerza la gratitud y la generosidad.",
            "Integra conocimiento y experiencia para guiar.",
            "Forma líderes y deja un impacto duradero.",
            "Vive su propósito y deja huella en la historia.",
            "Enseño, acompaño y dejo legado a otros.",
        ),
        "arbol_cosmico": (
            "frontend/assets/arbol_cosmico.json",
            "10. Árbol Cósmico (Unido al Universo)",
            "Alcanza la paz interior y plenitud del alma.",
            "Trasciende límites y comprende la verdad universal.",
            "Es faro de luz e inspiración para la humanidad.",
            "Conecta con la energía divina y el todo.",
            "Estoy en paz, en unidad y expando mi luz al universo.",
        ),
    }

    ruta_anim, titulo_fase, emo, men, soc, esp, frase = mapeo_bio.get(
        estado_limpio, mapeo_bio["semilla"]
    )

    animacion_json = cargar_lottie_local(ruta_anim)

    with col_img:
        if animacion_json:
            st_lottie(animacion_json, height=140, key=f"lottie_view_{estado_limpio}")
        else:
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
            icono_fallback = emojis_fase.get(estado_limpio, "🌱")
            st.markdown(
                "<h1 style='text-align: center; font-size: 75px; margin:"
                f" 0;'>{icono_fallback}</h1>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<p style='text-align: center; font-size: 14px; color: #4CAF50;"
            " font-weight: bold; margin-top: 5px;'>⚡ Energía Vital<br><span"
            f" style='font-size: 18px;'>{energia_vital} pts</span></p>",
            unsafe_allow_html=True,
        )

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

    # --- 2. INDICADORES VISUALES ---
    col1, col2 = st.columns(2)

    # =========================================================
# SECCIÓN: PASAPORTE DE NIVEL Y PROGRESO
# =========================================================
with col1:
    st.markdown("### 🎓 Pasaporte de Nivel")

    # --- VITRINA DE INSIGNIAS / MEDALLAS ---
    st.markdown("#### 🏅 Muro de Logros")

    # Aseguramos el cálculo de nivel_real para evitar el error en VS Code
    nivel_calculado = (
        (xp_actual // 100) + 1
        if "xp_actual" in locals()
        else st.session_state.get("nivel", 1)
    )

    # Evaluación de medallas ganadas
    medallas = (
        ["🛸 Primer Contacto", "🏅 Brote Explorador"]
        if nivel_calculado >= 3
        else ["🛸 Primer Contacto"]
    )

    if nivel_calculado >= 5:
        medallas.append("🌳 Líder Enraizado")

    col_medallas = st.columns(len(medallas))
    for idx, medalla in enumerate(medallas):
        with col_medallas[idx]:
            st.caption(f"✨ **{medalla}**")

    # 1. CÁLCULO DINÁMICO DEL NIVEL
    nivel_real = (xp_actual // 100) + 1

    # ---------------------------------------------------------
    # 🎯 PASO 2: DETECTOR DE ASCENSO DE NIVEL (UBICACIÓN AQUÍ)
    # ---------------------------------------------------------
    if "nivel_previo" not in st.session_state:
        st.session_state["nivel_previo"] = nivel_real

    # Dispara la celebración visual si el nivel actual es mayor al previo
    if nivel_real > st.session_state["nivel_previo"]:
        st.balloons()
        st.toast(f"🏆 ¡ASCENSO DE NIVEL! Ahora eres Nivel {nivel_real}", icon="🔥")
        st.info(
            f"✨ **¡Felicidades, Lindley!** Has alcanzado el **Nivel {nivel_real}**. Tu Bio-Estructura ha evolucionado."
        )
        st.session_state["nivel_previo"] = nivel_real
    # ---------------------------------------------------------

    # 2. CÁLCULO DE METRICAS VISUALES
    xp_inicio_nivel = (nivel_real - 1) * 100
    xp_meta_siguiente = nivel_real * 100

    xp_nivel_actual = max(0, xp_actual - xp_inicio_nivel)
    xp_requeridos_nivel = xp_meta_siguiente - xp_inicio_nivel
    xp_faltantes = max(0, xp_meta_siguiente - xp_actual)

    porcentaje_progreso = min(1.0, max(0.0, xp_nivel_actual / xp_requeridos_nivel))

    # 3. RENDERIZADO DE INTERFAZ
    st.metric(
        label="Ascenso de Nivel",
        value=f"Nivel {nivel_real}",
        delta=f"{xp_actual} XP Totales",
    )

    escalones = "🪜 " * nivel_real
    st.write(f"**Escalera de Progreso:** {escalones} 🧗")

    st.progress(porcentaje_progreso)

    st.markdown(
        f"""
        <p style='color: #FFFFFF; font-size: 16px; font-weight: bold; margin-top: 8px;'>
            🚀 Te faltan <span style='color: #00FFCC;'>{xp_faltantes} XP</span> para alcanzar el Nivel {nivel_real + 1}
        </p>
        """,
        unsafe_allow_html=True,
    )

    with col2:
        total_paginas = 5
        hojas_escritas = "📄 " * paginas_completadas
        hojas_vacias = "⬜ " * (total_paginas - paginas_completadas)

        st.markdown("### 📖 Libro Vivo")

        res_libro = requests.get(
            f"{API_URL}/usuarios/{usuario_id}/libro", headers=headers
        )
        capitulo = 1
        paginas = 1

        if res_libro.status_code == 200:
            datos_libro = res_libro.json()
            capitulo = datos_libro.get("capitulo_actual", 1)
            paginas = datos_libro.get("paginas_completadas", 1)

        st.metric(
            label="Progreso de Historia",
            value=f"Capítulo {capitulo}",
            delta=f"↑ {paginas}/5 Hojas Llenas",
        )

        iconos_paginas = "📄 " * paginas + "▫️ " * (5 - paginas)
        st.write(f"**Páginas Escribiéndose:** {iconos_paginas}")

        # --- EXPANDER PARA LEER PÁGINAS REALES GENERADAS ---
        with st.expander("📖 Leer las páginas de mi historia..."):
            st.info(f"**Capítulo {capitulo}: La Bitácora del Explorador**")

            # Consultamos las misiones completadas para reconstruir la historia
            res_misiones = requests.get(
                f"{API_URL}/usuarios/{usuario_id}/misiones/", headers=headers
            )

            if res_misiones.status_code == 200:
                misiones_list = res_misiones.json()
                completadas = [
                    m for m in misiones_list if m.get("estado") == "completada"
                ]

                if not completadas:
                    st.caption(
                        "Tu diario aún está en blanco. Completa misiones para escribir tus primeros capítulos."
                    )
                else:
                    for i, m in enumerate(completadas, start=1):
                        st.markdown(
                            f"""
                            **📄 Página {i}:** *Hito Alcanzado — {m.get("titulo_mision")}*  
                            > "{m.get("descripcion", "Evolución registrada en la bio-estructura.")}"
                            ---
                            """
                        )
            else:
                st.caption("Sincronizando el canal de lectura...")

    st.markdown("---")

    # --- PESTAÑAS DE INTERACCIÓN ---
    tab_chat, tab_misiones = st.tabs(
        ["👽 Contactar a XiXi", "🎯 Misiones de Evolución"]
    )

    # --- TAB 1: CHAT CON XIXI ---
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
                    "XiXi está decodificando tus frecuencias con Gemini..."
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
                        datos = res_chat.json()
                        respuesta = datos.get(
                            "respuesta_guia", "Frecuencia interrumpida."
                        )
                        xp_ganado = datos.get("xp_ganado", 0)
                        energia_ganada = datos.get("energia_ganada", 0)

                        mensaje_formateado = (
                            f"{respuesta}\n\n*(XiXi ha canalizado **+{xp_ganado} XP** a tu"
                            f" Pasaporte y **+{energia_ganada} pts** a tu Energía Vital)*"
                        )

                        st.markdown(mensaje_formateado)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": mensaje_formateado}
                        )

                        # --- NUEVA LÓGICA DE EVOLUCIÓN INTEGRADADA ---
                        try:
                            res_evo = requests.post(
                                f"{API_URL}/usuarios/{usuario_id}/evolucionar?xp_ganado={xp_ganado}",
                                headers=headers,
                                timeout=10,
                            )

                            if res_evo.status_code == 200:
                                datos_actualizados = res_evo.json()

                                # Actualizamos el estado de la sesión para la UI
                                st.session_state["xp_totales"] = datos_actualizados.get(
                                    "xp_totales"
                                )
                                st.session_state["nivel"] = datos_actualizados.get(
                                    "nivel_actual"
                                )

                                # Notificación visual del progreso
                                st.toast(
                                    f"✨ +{xp_ganado} XP Procesados | Nivel Actual: {st.session_state['nivel']}",
                                    icon="🚀",
                                )
                        except Exception as e:
                            st.error(f"Error de red al sincronizar evolución: {str(e)}")
                        # ---------------------------------------------

                        st.rerun()
                    else:
                        st.error("Anomalía detectada. No se pudo enlazar con XiXi.")

    # =========================================================
# SECCIÓN: LISTADO Y PROCESAMIENTO DE MISIONES PENDIENTES
# =========================================================
st.markdown("### 🎯 Desafíos de Sincronización")

# Botón para solicitar nueva misión
if st.button("👽 Solicitar Misión a XiXi (IA)"):
    res_ia = requests.post(
        f"{API_URL}/usuarios/{usuario_id}/misiones/generar_ia", headers=headers
    )
    if res_ia.status_code == 200:
        st.toast("✨ ¡Nueva Misión encomendada por XiXi!", icon="🛸")
        st.rerun()
    else:
        st.error("No se pudo conectar con el servidor de IA.")

# Consulta de misiones del usuario
res_misiones = requests.get(
    f"{API_URL}/usuarios/{usuario_id}/misiones/", headers=headers
)

if res_misiones.status_code == 200:
    misiones_lista = res_misiones.json()

    # Filtrar solo misiones en estado pendiente
    misiones_pendientes = [m for m in misiones_lista if m.get("estado") == "pendiente"]

    if not misiones_pendientes:
        st.info("No tienes desafíos pendientes. ¡Solicita uno nuevo a XiXi arriba! 🚀")
    else:
        # BUCLE CORRECTO: Itera cada misión pendiente individualmente
        for mision in misiones_pendientes:
            mision_id = mision.get("id")
            titulo = mision.get("titulo_mision", "Desafío de Evolución")
            recompensa = mision.get("recompensa_puntos", 50)

            col_info, col_btn = st.columns([3, 1])

            with col_info:
                st.markdown(
                    f"**{titulo}** | <span style='color: #00FFCC;'>+{recompensa} XP</span>",
                    unsafe_allow_html=True,
                )

            with col_btn:
                # El botón ahora reconoce la variable mision_id de forma limpia
                if st.button(f"Procesar #{mision_id}", key=f"btn_mision_{mision_id}"):
                    res_completar = requests.put(
                        f"{API_URL}/usuarios/{usuario_id}/misiones/{mision_id}/completar",
                        headers=headers,
                    )

                    if res_completar.status_code == 200:
                        st.balloons()
                        st.toast(
                            "🎉 ¡Desafío Sincronizado! Puntos de XP canalizados.",
                            icon="🚀",
                        )
                        st.rerun()
                    else:
                        st.error("⚠️ Error en la sincronización con el servidor.")

# =========================================================
# SECCIÓN: DASHBOARD DE ANALÍTICAS Y CRECIMIENTO HOLÍSTICO
# =========================================================
st.markdown("---")
st.markdown("### 📊 Dashboard de Crecimiento Holístico")
st.caption(
    "Visualización métrica del impacto de tus decisiones y misiones completadas."
)

# Calculamos los puntos holísticos basados en el XP total acumulado
xp_base = (
    xp_actual if "xp_actual" in locals() else st.session_state.get("xp_totales", 0)
)

pts_mental = int(xp_base * 0.30)
pts_emocional = int(xp_base * 0.25)
pts_social = int(xp_base * 0.25)
pts_espiritual = int(xp_base * 0.20)

# Renderizado de Tarjetas de Impacto en 4 Columnas
col_m, col_e, col_s, col_esp = st.columns(4)

with col_m:
    st.metric(
        label="🧠 Dimensión Mental",
        value=f"{pts_mental} pts",
        delta="Pensamiento Lógico",
    )
    st.progress(min(1.0, pts_mental / 200))

with col_e:
    st.metric(
        label="❤️ Dimensión Emocional",
        value=f"{pts_emocional} pts",
        delta="Resiliencia & Autocontrol",
    )
    st.progress(min(1.0, pts_emocional / 200))

with col_s:
    st.metric(
        label="👥 Dimensión Social",
        value=f"{pts_social} pts",
        delta="Liderazgo & Equipo",
    )
    st.progress(min(1.0, pts_social / 200))

with col_esp:
    st.metric(
        label="✨ Dimensión Espiritual",
        value=f"{pts_espiritual} pts",
        delta="Propósito & Valores",
    )
    st.progress(min(1.0, pts_espiritual / 200))

# Muestra del Balance General
with st.expander("📈 Ver desglose de balance analítico..."):
    st.write(
        f"""
        * **Índice de Madurez de Ingeniería:** `{pts_mental + pts_emocional} pts`
        * **Índice de Liderazgo Inspirador:** `{pts_social + pts_espiritual} pts`
        
        *Tu Bio-Estructura mantiene una tasa de equilibrio de crecimiento de un **{min(100, int((xp_base / 500) * 100))}%** respecto a la meta del Nivel Actual.*
        """
    )


# =========================================================
# 📜 CLASE DE DISEÑO PARA CERTIFICADO/REPORTE EJECUTIVO PDF
# =========================================================
class ReportePDF(FPDF):
    def header(self):
        # Membrete Superior Institucional
        self.set_fill_color(30, 41, 59)  # Azul Marino Corporativo
        self.rect(0, 0, 210, 20, "F")

        self.set_font("Helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(
            0, 10, "HISTORIAS QUE INSPIRAN(R) | CERTIFICADO DE EVOLUCION", align="L"
        )

        self.set_font("Helvetica", "", 8)
        self.set_xy(10, 11)
        self.cell(0, 10, "Sistema de Gamificacion & Desarrollo Holistico", align="L")
        self.ln(15)

    def footer(self):
        # Pie de Página Oficial
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(
            0,
            10,
            f"Documento de Progreso Oficial | Verificabilidad JWT | Pagina {self.page_no()}",
            align="C",
        )


def generar_pdf_certificado(
    nombre_usuario,
    usuario_id,
    nivel,
    xp_totales,
    fase_arbol,
    pts_m,
    pts_e,
    pts_s,
    pts_esp,
):
    pdf = ReportePDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    # Marco de Certificación Elegante
    pdf.set_draw_color(203, 213, 225)
    pdf.set_line_width(0.8)  # 🛠️ CORRECCIÓN: Método correcto para fpdf2
    pdf.rect(8, 25, 194, 257)

    # Título Principal
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        0, 10, "INFORME EJECUTIVO DE PROGRESO", align="C", new_x="LMARGIN", new_y="NEXT"
    )

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(
        0,
        5,
        "Acreditacion Gamificada de Habilidades y Competencias",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(8)

    # Bloque Datos del Usuario
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(15, 52, 180, 28, "F")

    pdf.set_xy(20, 56)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)

    nombre_limpio = str(nombre_usuario).upper()
    pdf.cell(80, 6, f"ESTUDIANTE: {nombre_limpio}")
    pdf.cell(
        80, 6, f"ID USUARIO: #{usuario_id}", align="R", new_x="LMARGIN", new_y="NEXT"
    )

    pdf.set_x(20)
    pdf.cell(80, 6, f"NIVEL ALCANZADO: Nivel {nivel} ({xp_totales} XP Totales)")
    pdf.cell(
        80, 6, f"BIO-ESTRUCTURA: {fase_arbol}", align="R", new_x="LMARGIN", new_y="NEXT"
    )
    pdf.ln(12)

    # Muro de Logros e Insignias
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "Muro de Logros Acreditados", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 65, 85)

    insignias = [" [X] Primer Contacto (Iniciacion en la Plataforma)"]
    if nivel >= 3:
        insignias.append(" [X] Brote Explorador (Constancia y Progreso)")
    if nivel >= 5:
        insignias.append(" [X] Lider Enraizado (Nivel 5 Alcanzado)")

    for ins in insignias:
        pdf.cell(0, 6, f"   {ins}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # Matriz de Competencias Holísticas (Tabla Estructurada)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "Matriz de Competencias Holisticas", new_x="LMARGIN", new_y="NEXT")

    # Encabezados de Tabla
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(70, 8, " Dimension", border=1, fill=True)
    pdf.cell(40, 8, " Puntaje", border=1, fill=True, align="C")
    pdf.cell(
        70,
        8,
        " Enfoque Estrategico",
        border=1,
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # Filas de la Tabla
    datos_tabla = [
        ("Dimension Mental", f"{pts_m} pts", "Pensamiento Logico & Arquitectura"),
        ("Dimension Emocional", f"{pts_e} pts", "Resiliencia & Autocontrol"),
        ("Dimension Social", f"{pts_s} pts", "Liderazgo & Trabajo en Equipo"),
        ("Dimension Espiritual", f"{pts_esp} pts", "Proposito de Vida & Valores"),
    ]

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.set_fill_color(248, 250, 252)

    for i, (dim, pts, enf) in enumerate(datos_tabla):
        fill = i % 2 == 0
        pdf.cell(70, 7, f" {dim}", border=1, fill=fill)
        pdf.cell(40, 7, f"{pts}", border=1, fill=fill, align="C")
        pdf.cell(70, 7, f" {enf}", border=1, fill=fill, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)

    # Sello de Autenticidad Digital
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(
        0,
        5,
        "FIRMA DIGITAL Y EMBLEMA DE AUTENTICIDAD",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(
        0, 4, "Historias que Inspiran(R) - Todos los derechos reservados.", align="C"
    )

    return bytes(pdf.output())


# =========================================================
# RENDERING EN FRONTEND DE STREAMLIT
# =========================================================
st.markdown("---")
st.markdown("### 📜 Certificación y Reporte de Progreso")

col_rep1, col_rep2 = st.columns([2, 1])

with col_rep1:
    st.write(
        """
        Genera tu **Certificado Oficial de Evolución** en formato PDF con membrete institucional. 
        Este documento acredita tu nivel, las insignias obtenidas y la matriz de competencias 
        cuadridimensional alcanzada.
        """
    )

with col_rep2:
    try:
        # Calculamos el nivel dinámico antes de llamar la función PDF
        nivel_real = (xp_base // 100) + 1

        pdf_bytes = generar_pdf_certificado(
            nombre_usuario=st.session_state.get("nombre_usuario", "Lindley"),
            usuario_id=st.session_state.get("usuario_id", 1),
            nivel=nivel_real,  # 👈 Sincronización exacta con los 305 XP
            xp_totales=xp_base,
            fase_arbol=st.session_state.get("fase_arbol", "1. Semilla"),
            pts_m=pts_mental,
            pts_e=pts_emocional,
            pts_s=pts_social,
            pts_esp=pts_espiritual,
        )

        st.download_button(
            label="📄 Descargar Certificado Oficial (.PDF)",
            data=pdf_bytes,
            file_name=f"Certificado_Evolucion_{st.session_state.get('nombre_usuario', 'Lindley')}.pdf",
            mime="application/pdf",
            key="btn_download_pdf",
        )
    except Exception as e:
        st.error(f"Error al generar el PDF de certificación: {e}")
