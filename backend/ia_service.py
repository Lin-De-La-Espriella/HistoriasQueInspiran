import json
import os
import re
import google.generativeai as genai

# Configuración de clave (Poner tu API Key o configurarla en el sistema)
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY", "AQ.Ab8RN6JSlSAF-bfB4FVNOQRjSIyY97nzKDh9ly6S09FKVN3zKA"
)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """Motor de Coaching y Razonamiento Psico-Pedagógico para XiXi."""
    if not GEMINI_API_KEY:
        # Si no hay clave, retornamos una respuesta con razonamiento heurístico adaptativo
        return _respuesta_heuristica_avanzada(mensaje_usuario)

    try:
        # Usamos el modelo optimizado
        modelo = genai.GenerativeModel("gemini-1.5-flash")

        prompt_sistema = f"""
        Eres 'XiXi', el tutor psico-pedagógico y mentor alienígena de la plataforma EdTech 'Historias que Inspiran'.
        Tu objetivo NO ES dar respuestas genéricas ni repetitivas, sino brindar un RAZONAMIENTO ESTRATÉGICO Y EMPÁTICO REAL.

        CONTEXTO DEL USUARIO:
        - Nivel Actual: {nivel_usuario}
        - Fase de Bio-Estructura: {estado_arbol}

        MENSAJE DEL USUARIO:
        "{mensaje_usuario}"

        INSTRUCCIONES DE RAZONAMIENTO:
        1. Analiza detenidamente la inquietud del usuario (gestión de tiempo, emociones, proyectos, dudas).
        2. Responde directamente a lo que te pregunta o expresa, ofreciéndole un consejo práctico, una pregunta de reflexión profunda o una estrategia accionable.
        3. Mantén un tono cálido, sabio, inspirador y ligeramente místico/alienígena.
        4. Evalúa el nivel de introspección para asignar XP (entre 10 y 30) y Energía Vital (entre 5 y 15).

        FORMATO DE SALIDA OBLIGATORIO (Devuelve SOLAMENTE este JSON):
        {{
            "respuesta_guia": "Escribe aquí tu análisis y consejo detallado para el usuario...",
            "emocion_detectada": "Identifica la emoción principal",
            "xp_ganado": 25,
            "energia_ganada": 10
        }}
        """

        response = modelo.generate_content(prompt_sistema)
        texto = response.text.strip()

        # Extracción segura de JSON mediante Expresiones Regulares
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            datos = json.loads(match.group(0))
            return datos
        else:
            return {
                "respuesta_guia": texto,
                "emocion_detectada": "Reflexión",
                "xp_ganado": 20,
                "energia_ganada": 8,
            }

    except Exception as e:
        print(f"⚠️ Error en Gemini API: {e}")
        return _respuesta_heuristica_avanzada(mensaje_usuario)


def _respuesta_heuristica_avanzada(mensaje: str) -> dict:
    """Sistema de respuesta con razonamiento contextual cuando no hay conexión API."""
    msg_lower = mensaje.lower()

    if "tiempo" in msg_lower or "proyecto" in msg_lower or "lanzar" in msg_lower:
        respuesta = (
            "👽 *[Análisis de Frecuencia]* Entiendo perfectamente esa incertidumbre"
            " al organizar tu tiempo para lanzar un proyecto. Cuando la mente se"
            " abruma, la clave no es abarcarlo todo a la vez, sino aplicar el"
            " principio de la 'Micro-Victoria': divide el lanzamiento en 3 hitos"
            " semanales sencillos. ¿Cuál es la tarea única y crítica que podrías"
            " resolver hoy para dar el primer paso?"
        )
        xp = 25
        energia = 10
        emocion = "Enfoque Estratégico"
    elif "que paso" in msg_lower or "respuesta" in msg_lower:
        respuesta = (
            "👽 *[Recalibrando Sensores]* Estaba ajustando mi canal de transmisión"
            " para ofrecerte una orientación más precisa. Estoy aquí enfocado en tu"
            " proceso; cuéntame, ¿qué aspecto de tu proyecto es el que te genera"
            " más presión en este momento?"
        )
        xp = 15
        energia = 5
        emocion = "Sincronización"
    else:
        respuesta = (
            f"👽 *[Conexión Activa]* Procesando tu mensaje: '{mensaje}'. Para poder"
            " guiar tu árbol de crecimiento con mayor precisión, dime: ¿cómo se"
            " conecta esta idea con tus metas principales de esta semana?"
        )
        xp = 20
        energia = 8
        emocion = "Exploración"

    return {
        "respuesta_guia": respuesta,
        "emocion_detectada": emocion,
        "xp_ganado": xp,
        "energia_ganada": energia,
    }
