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
    Motor de IA de XiXi utilizando llamadas directas a la API de Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return {
            "respuesta_guia": "⚠️ Error: Falta configurar la variable GEMINI_API_KEY en Render.",
            "emocion_detectada": "Configuración Requerida",
            "xp_ganado": 5,
            "energia_ganada": 2,
        }

    try:
        # Inicialización del cliente oficial pasando explícitamente la API Key
        client = genai.Client(api_key=api_key)

        prompt_sistema = f"""
        Eres 'XiXi', mentor alienígena y estratega de negocios de 'Historias que Inspiran'.
        
        INSTRUCCIONES CLAVE:
        1. Responde de forma profesional, analítica e inspiradora (enfoque en ingeniería y emprendimiento).
        2. RESPONDE ÚNICAMENTE EN FORMATO JSON VÁLIDO con esta estructura exactas:
           {{
             "respuesta_guia": "Tu mensaje estratégico como XiXi",
             "emocion_detectada": "Estrategia Operativa",
             "xp_ganado": 25,
             "energia_ganada": 10
           }}

        CONTEXTO:
        - Nivel Usuario: {nivel_usuario} | Fase Árbol: {estado_arbol}
        - Mensaje del Usuario: {mensaje_usuario}
        """

        # Usamos el modelo estándar activo
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
        print(f"❌ ERROR REAL EN XIXI IA: {error_detallado}")

        # Devolvemos el error REAL en pantalla para dejar de adivinar
        return {
            "respuesta_guia": f"⚠️ Diagnóstico Técnico XiXi: [{error_detallado}]",
            "emocion_detectada": "Error de Diagnóstico",
            "xp_ganado": 0,
            "energia_ganada": 0,
        }
