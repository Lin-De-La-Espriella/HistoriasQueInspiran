import json
import os
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """
    Motor de IA de XiXi utilizando el SDK oficial y moderno 'google-genai'
    con el modelo 'gemini-2.0-flash'.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return {
            "respuesta_guia": "⚠️ Error de Configuración: La variable 'GEMINI_API_KEY' no fue encontrada en el entorno de Render.",
            "emocion_detectada": "Configuración Requerida",
            "xp_ganado": 5,
            "energia_ganada": 2,
        }

    try:
        # Inicialización del cliente oficial moderno
        client = genai.Client(api_key=api_key)

        prompt_sistema = f"""
        Eres 'XiXi', mentor alienígena y estratega de negocios de 'Historias que Inspiran'.
        
        INSTRUCCIONES CLAVE:
        1. Proporciona respuestas profesionales, analíticas e inspiradoras enfocadas en ingeniería y emprendimiento.
        2. DEBES RESPONDER EXCLUSIVAMENTE EN FORMATO JSON VÁLIDO con las claves exactas:
           {{
             "respuesta_guia": "Tu respuesta estratégica como XiXi",
             "emocion_detectada": "Estrategia Operativa",
             "xp_ganado": 25,
             "energia_ganada": 10
           }}

        CONTEXTO:
        - Nivel Usuario: {nivel_usuario} | Fase Árbol: {estado_arbol}
        - Mensaje del Usuario: {mensaje_usuario}
        """

        # Generación con el modelo moderno de producción
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_sistema,
        )

        texto_respuesta = response.text.strip()

        # Extracción limpia de JSON
        match = re.search(r"\{.*\}", texto_respuesta, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            return {
                "respuesta_guia": texto_respuesta,
                "emocion_detectada": "Análisis Estratégico",
                "xp_ganado": 25,
                "energia_ganada": 10,
            }

    except Exception as e:
        error_detallado = str(e)
        print(f"❌ Error en Gemini GenAI API: {error_detallado}")
        return {
            "respuesta_guia": f"⚠️ Fallo de Conexión Gemini GenAI: [{error_detallado}]",
            "emocion_detectada": "Diagnóstico de Red",
            "xp_ganado": 10,
            "energia_ganada": 5,
        }
