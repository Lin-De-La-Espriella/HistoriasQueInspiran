import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """
    Motor de IA de XiXi utilizando el SDK estable de google-generativeai
    con respaldo dinámico y estructurado.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        print(
            "❌ ALERTA: La variable GEMINI_API_KEY no está configurada en el entorno."
        )
        return {
            "respuesta_guia": f"Saludos, Lindley. He registrado tu transmisión ('{mensaje_usuario}'), pero la clave de IA (GEMINI_API_KEY) no está activa en las variables de entorno de Render.",
            "emocion_detectada": "Alerta de Configuración",
            "xp_ganado": 15,
            "energia_ganada": 5,
        }

    try:
        genai.configure(api_key=api_key)

        prompt_sistema = f"""
        Eres 'XiXi', mentor alienígena y estratega de negocios de 'Historias que Inspiran'.
        
        INSTRUCCIONES CLAVE:
        1. Si el usuario pide un formato, estructura o guía, proveylo de forma detallada, profesional y orientada a ingeniería y emprendimiento.
        2. Mantén un tono motivador, analítico y estratégico.
        3. DEBES RESPONDER EXCLUSIVAMENTE EN FORMATO JSON VÁLIDO con las siguientes claves exactas:
           {{
             "respuesta_guia": "Tu respuesta estructurada y profesional como XiXi",
             "emocion_detectada": "Estrategia Operativa",
             "xp_ganado": 25,
             "energia_ganada": 10
           }}

        CONTEXTO ACTUAL:
        - Nivel del Usuario: {nivel_usuario}
        - Estado del Árbol: {estado_arbol}
        - Mensaje del Usuario: {mensaje_usuario}
        """

        # Usar el modelo estable y universal de Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_sistema)
        texto_respuesta = response.text.strip()

        # Extracción segura de JSON mediante expresiones regulares
        match = re.search(r"\{.*\}", texto_respuesta, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            return {
                "respuesta_guia": texto_respuesta,
                "emocion_detectada": "Estrategia Operativa",
                "xp_ganado": 25,
                "energia_ganada": 10,
            }

    except Exception as e:
        print(f"❌ Error crítico en motor Gemini: {str(e)}")
        return {
            "respuesta_guia": (
                f"Saludos, Lindley. He decodificado tu mensaje ('{mensaje_usuario}'). "
                "Como estratega, te sugiero estructurar este proceso bajo un enfoque de "
                "mejora continua y modelado lógico. (Nota técnica: Error de conexión con IA)."
            ),
            "emocion_detectada": "Resiliencia Operativa",
            "xp_ganado": 20,
            "energia_ganada": 10,
        }
