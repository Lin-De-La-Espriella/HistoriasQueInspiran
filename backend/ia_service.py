import json
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """
    Motor de IA de XiXi con manejo inteligente de cuota y fallback de modelo.
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

        # Intento con modelo principal
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt_sistema,
            )
        except APIError as e:
            # Si se agota la cuota (429), reintentamos con gemini-2.0-flash-lite
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(
                    "⚠️ Cuota agotada en 2.0-flash, alternando a gemini-2.0-flash-lite..."
                )
                response = client.models.generate_content(
                    model="gemini-2.0-flash-lite",
                    contents=prompt_sistema,
                )
            else:
                raise e

        texto_respuesta = response.text.strip()

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

        if "RESOURCE_EXHAUSTED" in error_detallado or "429" in error_detallado:
            return {
                "respuesta_guia": "🚀 Canal de transmisión saturado momentáneamente por alta frecuencia de datos. XiXi está recalibrando sus sensores. Por favor intenta tu mensaje nuevamente en 1 minuto.",
                "emocion_detectada": "Enfriamiento de Canales",
                "xp_ganado": 10,
                "energia_ganada": 5,
            }

        return {
            "respuesta_guia": f"⚠️ Fallo de Conexión Gemini GenAI: [{error_detallado}]",
            "emocion_detectada": "Diagnóstico de Red",
            "xp_ganado": 10,
            "energia_ganada": 5,
        }
