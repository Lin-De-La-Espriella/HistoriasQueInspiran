"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / WEB
Aplicación Web Principal (Streamlit Interface)
===============================================================================
"""
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Configuración de página con estética Gamificada
st.set_page_config(
    page_title="Historias que Inspiran®",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Detecta si está en desarrollo local o en la nube
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Manejo de Estado de Sesión Local
if "token" not in st.session_state:
    st.session_state.token = None
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# Custom CSS / Estilos
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; color: #00FFCC; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1E293B; color: #FFF; }
    </style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Pantalla de Login / Registro
# -----------------------------------------------------------------------------
def pantalla_autenticacion():
    st.sidebar.title("🔐 Acceso al Universo")
    modo = st.sidebar.radio("Elige una opción:", ["Iniciar Sesión", "Registrarse"])
    
    email = st.sidebar.text_input("Correo electrónico", key="auth_email")
    password = st.sidebar.text_input("Contraseña", type="password", key="auth_pass")

    if modo == "Registrarse":
        nombre = st.sidebar.text_input("Nombre completo", key="auth_nombre")
        if st.sidebar.button("Crear Cuenta"):
            try:
                res = requests.post(
                    f"{API_URL}/auth/registro",
                    json={"nombre": nombre, "email": email, "password": password},
                    timeout=5
                )
                if res.status_code == 201:
                    st.sidebar.success("¡Cuenta creada exitosamente! Ahora inicia sesión.")
                else:
                    st.sidebar.error(res.json().get("detail", "Error al registrar."))
            except requests.exceptions.ConnectionError:
                st.sidebar.error("No se pudo conectar con el servidor backend. Verifica que esté encendido.")

    elif modo == "Iniciar Sesión":
        if st.sidebar.button("Entrar al Juego"):
            try:
                res = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password},
                    timeout=5
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["access_token"]
                    st.sidebar.success("¡Bienvenido de nuevo!")
                    st.rerun()
                else:
                    st.sidebar.error("Credenciales inválidas o correo no registrado.")
            except requests.exceptions.ConnectionError:
                st.sidebar.error("No se pudo conectar con el servidor backend (API apagada).")


# -----------------------------------------------------------------------------
# Panel Principal (Dashboard del Emprendedor)
# -----------------------------------------------------------------------------
def panel_principal():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    try:
        res_user = requests.get(f"{API_URL}/usuario/perfil", headers=headers, timeout=5)
        if res_user.status_code != 200:
            st.error("Sesión expirada. Inicia sesión de nuevo.")
            st.session_state.token = None
            st.rerun()
            return

        usuario = res_user.json()
        st.title(f"🌱 ¡Hola, {usuario['nombre']}!")
        st.caption("Bienvenido a la Aventura de Transformación Emprendedora.")

        col1, col2, col3 = st.columns(3)
        
        # Pasaporte
        res_pasaporte = requests.get(f"{API_URL}/usuario/pasaporte", headers=headers, timeout=5).json()
        with col1:
            st.subheader("📜 Pasaporte")
            st.write(f"**Nivel:** {res_pasaporte.get('nivel_actual', 1)}")
            st.write(f"**Experiencia:** {res_pasaporte.get('puntos_experiencia', 0)} XP")

        # Árbol
        res_arbol = requests.get(f"{API_URL}/usuario/arbol", headers=headers, timeout=5).json()
        with col2:
            st.subheader("🌳 Árbol de Progreso")
            st.write(f"**Estado:** {res_arbol.get('estado_crecimiento', 'Semilla')}")
            st.progress(res_arbol.get('energia_vital', 100) / 100)

        # Libro Vivo
        res_libro = requests.get(f"{API_URL}/usuario/libro", headers=headers, timeout=5).json()
        with col3:
            st.subheader("📖 Libro Vivo")
            st.write(f"**Capítulo Actual:** {res_libro.get('capitulo_actual', 1)}")
            st.write(f"**Páginas:** {res_libro.get('paginas_completadas', 0)}")

    except requests.exceptions.ConnectionError:
        st.error("Se perdió la conexión con el servidor backend.")

    st.divider()
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.token = None
        st.rerun()


# Renderizado según estado de sesión
if not st.session_state.token:
    pantalla_autenticacion()
    st.info("👈 Inicia sesión en el panel lateral para entrar al universo.")
else:
    panel_principal()