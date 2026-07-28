"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / WEB
Aplicación Web Principal (Dashboard + Personajes XiXi & Dudi)
===============================================================================
"""

import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Historias que Inspiran®",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ❌ Elimina esta línea:
# API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# ✅ Reemplázala por este bloque (Prioridad a la Nube):
try:
    # 1. Intenta leer el Secret configurado en Streamlit Cloud
    API_URL = st.secrets["API_URL"].rstrip("/")
except Exception:
    # 2. Si falla (desarrollo local), usa la variable de entorno
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
CACHE_FILE = os.path.join(os.path.dirname(__file__), ".session_cache.json")


def guardar_sesion_local(token: str, email: str):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"access_token": token, "email": email}, f)
    except Exception:
        pass


def cargar_sesion_local():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("access_token"), data.get("email")
        except Exception:
            return None, None
    return None, None


def cerrar_sesion_local():
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except Exception:
            pass
    st.session_state.token = None
    st.session_state.email = None


if "token" not in st.session_state or not st.session_state.token:
    token_guardado, email_guardado = cargar_sesion_local()
    st.session_state.token = token_guardado
    st.session_state.email = email_guardado


def pantalla_autenticacion():
    st.sidebar.title("🔐 Acceso al Universo")
    modo = st.sidebar.radio("Elige una opción:", ["Iniciar Sesión", "Registrarse"])

    with st.sidebar.form(key="form_autenticacion"):
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")

        if modo == "Registrarse":
            nombre = st.text_input("Nombre completo")
        else:
            nombre = ""

        recordar = st.checkbox("Recordar sesión en este equipo", value=True)
        submit_btn = st.form_submit_button(label="Entrar / Crear Cuenta")

    if submit_btn:
        if not email or not password:
            st.sidebar.warning("⚠️ Por favor, completa el correo y la contraseña.")
            return

        if modo == "Registrarse":
            if not nombre:
                st.sidebar.warning("⚠️ Por favor, ingresa tu nombre completo.")
                return

            try:
                res = requests.post(
                    f"{API_URL}/auth/registro",
                    json={"nombre": nombre, "email": email, "password": password},
                    timeout=5,
                )
                if res.status_code == 201:
                    st.sidebar.success(
                        "🌱 ¡Cuenta creada exitosamente! Cambia arriba a 'Iniciar Sesión' para entrar."
                    )
                else:
                    try:
                        error_msg = res.json().get("detail", "Error al registrar.")
                    except ValueError:
                        error_msg = f"Error Interno ({res.status_code})."
                    st.sidebar.error(error_msg)
            except requests.exceptions.ConnectionError:
                st.sidebar.error("❌ No se pudo conectar con el servidor backend.")

        elif modo == "Iniciar Sesión":
            try:
                res = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password},
                    timeout=5,
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.email = email
                    if recordar:
                        guardar_sesion_local(data["access_token"], email)
                    st.sidebar.success("¡Bienvenido de nuevo!")
                    st.rerun()
                else:
                    st.sidebar.error(
                        "❌ Credenciales inválidas o correo no registrado."
                    )
            except requests.exceptions.ConnectionError:
                st.sidebar.error("❌ No se pudo conectar con el servidor backend.")


def panel_principal():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = []

    try:
        res_user = requests.get(
            f"{API_URL}/usuario/perfil", headers=headers, timeout=15
        )
        if res_user.status_code != 200:
            st.error("La sesión ha expirado.")
            cerrar_sesion_local()
            st.rerun()
            return

        usuario = res_user.json()
        st.title(f"🌱 ¡Hola, {usuario['nombre']}!")
        st.caption("Bienvenido a la Aventura de Transformación Emprendedora.")

        # --- Fila 1: Métricas del Ecosistema ---
        col1, col2, col3 = st.columns(3)

        res_pasaporte = requests.get(
            f"{API_URL}/usuario/pasaporte", headers=headers, timeout=10
        )
        data_pasaporte = (
            res_pasaporte.json()
            if res_pasaporte.status_code == 200 and res_pasaporte.text
            else {}
        )
        if not isinstance(data_pasaporte, dict):
            data_pasaporte = {}

        with col1:
            st.subheader("📜 Pasaporte")
            st.write(f"**Nivel:** {data_pasaporte.get('nivel_actual', 1)}")
            st.write(
                f"**Experiencia:** {data_pasaporte.get('puntos_experiencia', 0)} XP"
            )

        res_arbol = requests.get(
            f"{API_URL}/usuario/arbol", headers=headers, timeout=10
        )
        data_arbol = (
            res_arbol.json() if res_arbol.status_code == 200 and res_arbol.text else {}
        )
        if not isinstance(data_arbol, dict):
            data_arbol = {}

        with col2:
            st.subheader("🌳 Árbol de Progreso")
            st.write(f"**Estado:** {data_arbol.get('estado_crecimiento', 'semilla')}")
            st.progress(data_arbol.get("energia_vital", 100) / 100)

        res_libro = requests.get(
            f"{API_URL}/usuario/libro", headers=headers, timeout=10
        )
        data_libro = (
            res_libro.json() if res_libro.status_code == 200 and res_libro.text else {}
        )
        if not isinstance(data_libro, dict):
            data_libro = {}

        capitulo_actual = data_libro.get("capitulo_actual", 1)
        with col3:
            st.subheader("📖 Libro Vivo")
            st.write(f"**Capítulo Actual:** {capitulo_actual}")
            st.write(f"**Páginas:** {data_libro.get('paginas_completadas', 0)}")

        st.divider()

        # --- Fila 2: Pestañas de Interacción ---
        tab_personajes, tab_capitulo, tab_libro_visor = st.tabs(
            ["💬 Hablar con XiXi & Dudi", "🚀 Forjar Capítulo Vivo", "📖 Mi Libro Vivo"]
        )

        # --- Módulo 1: Chat ---
        with tab_personajes:
            st.subheader("Selecciona tu Guía de Aventura")
            personaje = st.radio(
                "¿Con quién deseas conversar?",
                ["XiXi (Inspiración y Guía)", "Dudi (Voz de la Duda y Reflexión)"],
                horizontal=True,
            )
            nombre_personaje = "xixi" if "XiXi" in personaje else "dudi"
            avatar_emoji = "🌟" if nombre_personaje == "xixi" else "☁️"

            st.markdown("---")

            for msg in st.session_state.mensajes_chat:
                avatar = "🧑‍💻" if msg["role"] == "user" else msg.get("avatar", "🌟")
                st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

            prompt_ninio = st.chat_input(
                f"Escríbele un mensaje a {'XiXi 🌟' if nombre_personaje == 'xixi' else 'Dudi ☁️'}..."
            )

            if prompt_ninio:
                st.session_state.mensajes_chat.append(
                    {"role": "user", "content": prompt_ninio}
                )
                try:
                    res_chat = requests.post(
                        f"{API_URL}/ia/conversar",
                        headers=headers,
                        json={"personaje": nombre_personaje, "mensaje": prompt_ninio},
                        timeout=15,
                    )
                    if res_chat.status_code == 200:
                        st.session_state.mensajes_chat.append(
                            {
                                "role": "assistant",
                                "content": res_chat.json().get("respuesta"),
                                "avatar": avatar_emoji,
                            }
                        )
                    else:
                        st.session_state.mensajes_chat.append(
                            {
                                "role": "assistant",
                                "content": f"⚠️ Error {res_chat.status_code}: No pude procesar el mensaje.",
                                "avatar": avatar_emoji,
                            }
                        )
                except Exception:
                    st.session_state.mensajes_chat.append(
                        {
                            "role": "assistant",
                            "content": "⚡ Error de conexión con el Bosque de las Ideas.",
                            "avatar": avatar_emoji,
                        }
                    )
                st.rerun()

        # --- Módulo 2: Forjado ---
        with tab_capitulo:
            st.write(
                f"Estás creando la historia para tu **Capítulo {capitulo_actual}**."
            )

            with st.form("form_ia_capitulo"):
                empresa = st.text_input(
                    "¿Cómo se llama tu emprendimiento o idea de proyecto?",
                    value="Maison Zerda",
                )
                proposito = st.text_area(
                    "¿Cuál es el propósito o visión principal de tu idea?",
                    value="Crear una marca de perfumería de lujo inspirada en la historia de Cartagena.",
                )
                btn_generar = st.form_submit_button("🚀 Forjar Capítulo con IA")

            if btn_generar:
                with st.spinner(
                    "El motor de IA está tejiendo tu capítulo y calculando tus recompensas..."
                ):
                    try:
                        res_ia = requests.post(
                            f"{API_URL}/ia/generar-capitulo",
                            headers=headers,
                            json={
                                "capitulo": capitulo_actual,
                                "respuestas_usuario": {
                                    "nombre_empresa": empresa,
                                    "proposito": proposito,
                                },
                            },
                            timeout=40,
                        )

                        if res_ia.status_code == 200:
                            resultado = res_ia.json()
                            puntos_ganados = resultado.get("puntos_otorgados", 50)

                            st.balloons()
                            st.snow()

                            st.markdown(
                                f"""
                                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0px 4px 15px rgba(56, 239, 125, 0.3);">
                                    <h2 style="margin: 0; color: white;">🎉 ¡FELICITACIONES, CREADOR! 🎉</h2>
                                    <h3 style="margin: 10px 0 0 0; color: white;">🌟 ¡GANASTE +{puntos_ganados} XP! 🌟</h3>
                                    <p style="margin: 5px 0 0 0; font-size: 1.1em;">Tu Árbol de Progreso ha recibido Energía Vital 🌳✨</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.info(
                                f"📖 **Tu Historia Forjada:**\n\n{resultado.get('historia_narrativa')}"
                            )

                            # Eliminada la redundancia de la misión: Solo se renderiza la tarjeta HTML
                            mision = resultado.get(
                                "mision_sugerida",
                                "Sigue conversando con XiXi y Dudi para descubrir más.",
                            )
                            st.markdown(
                                f"""
                                <div style="background: #1e293b; border-left: 5px solid #f59e0b; padding: 15px; border-radius: 8px; margin-top: 15px;">
                                    <h4 style="margin: 0; color: #f59e0b;">🎯 PRÓXIMA MISIÓN DE CREADOR:</h4>
                                    <p style="margin: 8px 0 0 0; font-size: 1.05em; color: #f8fafc;">{mision}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.markdown("---")
                            st.subheader("🎯 Entregar Misión Activa")
                            with st.form("form_entrega_mision"):
                                respuesta_mision = st.text_area(
                                    "Escribe aquí tu avance o solución a la misión asignada:",
                                    placeholder="Ejemplo: Las 3 notas de mi perfume serán Jazmín de San Diego, Brisa Marina y Cedro...",
                                )
                                btn_entregar = st.form_submit_button(
                                    "🌟 Entregar Misión y Reclamar +30 XP"
                                )

                                if btn_entregar and respuesta_mision.strip():
                                    with st.spinner("XiXi está evaluando tu avance..."):
                                        res_mision = requests.post(
                                            f"{API_URL}/ia/validar-mision",
                                            headers=headers,
                                            json={
                                                "mision": mision,
                                                "respuesta_usuario": respuesta_mision,
                                            },
                                            timeout=20,
                                        )
                                        if res_mision.status_code == 200:
                                            eval_data = res_mision.json()
                                            st.balloons()
                                            st.success(
                                                f"🎉 ¡Misión Completada! +{eval_data.get('puntos_otorgados', 30)} XP Ganados"
                                            )
                                            st.info(
                                                f"🌟 **Feedback de XiXi:** {eval_data.get('feedback')}"
                                            )
                                        else:
                                            st.error(
                                                "Hubo un problema al validar la misión."
                                            )
                        else:
                            st.error(f"Hubo un error en el servidor: {res_ia.text}")

                    except requests.exceptions.Timeout:
                        st.error(
                            "⏳ El motor de IA se tomó demasiado tiempo en pensar. Revisa tu Pasaporte."
                        )
                    except requests.exceptions.RequestException:
                        st.error(
                            "⚡ Hubo un pequeño corte de conexión con el Bosque de las Ideas. Intenta nuevamente."
                        )

            st.divider()
            if st.button("✨ Ver mi nuevo nivel en el Pasaporte"):
                st.rerun()

        # --- Módulo 3: Visor del Libro Vivo (Optimizado Bajo Demanda) ---
        with tab_libro_visor:
            st.subheader("📚 Tu Libro Vivo de Emprendimiento")
            st.caption(
                "Aquí se conservan las historias y decisiones que forjan tu camino como creador."
            )

            historial_capitulos = data_libro.get("capitulos_narrativos", [])
            resumen_adn = data_libro.get("resumen_adn", {})

            if not historial_capitulos:
                st.info(
                    "Aún no has forjado ningún capítulo. ¡Ve a la pestaña 'Forjar Capítulo Vivo' para escribir tu primera página!"
                )
            else:
                col_hist, col_adn = st.columns([2, 1])

                with col_hist:
                    st.write("### 📖 Capítulos Escritos")
                    for idx, cap in enumerate(reversed(historial_capitulos), start=1):
                        num_cap = cap.get(
                            "capitulo", len(historial_capitulos) - idx + 1
                        )
                        with st.expander(
                            f"Capítulo {num_cap}: La Historia de {resumen_adn.get('nombre_empresa', 'Tu Idea')}",
                            expanded=(idx == 1),
                        ):
                            st.write(cap.get("narrativa", "Sin narrativa disponible."))

                with col_adn:
                    st.write("### 🧬 ADN de tu Proyecto")
                    st.success(
                        f"**Empresa / Idea:**\n{resumen_adn.get('nombre_empresa', 'No definido')}"
                    )
                    st.info(
                        f"**Propósito Principal:**\n{resumen_adn.get('proposito', 'No definido')}"
                    )

                # Lógica corregida para generar el PDF únicamente al presionar el botón
                st.divider()
                st.write("### 📥 Exportar tu Obra")

                if "pdf_data" not in st.session_state:
                    st.session_state.pdf_data = None

                col_btn1, col_btn2 = st.columns([1, 2])
                with col_btn1:
                    if st.button(
                        "📄 Prepara mi Libro en PDF", use_container_width=True
                    ):
                        with st.spinner("Compilando..."):
                            try:
                                res_pdf = requests.get(
                                    f"{API_URL}/usuario/libro/pdf",
                                    headers=headers,
                                    timeout=15,
                                )
                                if res_pdf.status_code == 200:
                                    st.session_state.pdf_data = res_pdf.content
                                    st.success("¡PDF listo!")
                                else:
                                    st.error("Error al generar PDF en el servidor.")
                            except requests.exceptions.RequestException:
                                st.error("Error de conexión al solicitar el PDF.")

                if st.session_state.pdf_data is not None:
                    with col_btn2:
                        st.download_button(
                            label="⬇️ Guardar Archivo PDF",
                            data=st.session_state.pdf_data,
                            file_name=f"Libro_Vivo_{resumen_adn.get('nombre_empresa', 'Emprendedor')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )

    except requests.exceptions.ConnectionError:
        st.error("Se perdió la conexión con el servidor backend.")

    st.divider()
    if st.sidebar.button("🔒 Cerrar Sesión"):
        cerrar_sesion_local()
        st.rerun()


# =======================================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# =======================================================
if "token" not in st.session_state:
    st.session_state.token = None

st.title("🌱 Historias que Inspiran®")
st.caption("Descubre tu talento. Crea soluciones. Inspira al mundo. 🚀")

if not st.session_state.token:
    pantalla_autenticacion()
    st.info("👈 Inicia sesión o regístrate en el panel lateral para continuar.")
else:
    panel_principal()
