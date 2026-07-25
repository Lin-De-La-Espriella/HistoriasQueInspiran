import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """
    Motor de IA de XiXi utilizando la infraestructura ultra rápida de Groq Cloud.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        return {
            "respuesta_guia": "⚠️ Error de Configuración: No se encontró la variable GROQ_API_KEY en el entorno.",
            "emocion_detectada": "Configuración Requerida",
            "xp_ganado": 5,
            "energia_ganada": 2,
        }

    try:
        client = Groq(api_key=api_key)

        prompt_sistema = f"""
        Eres 'XiXi', mentor alienígena y estratega de negocios de 'Historias que Inspiran'.
        
        INSTRUCCIONES CLAVE:
        1. Proporciona respuestas profesionales, analíticas e inspiradoras enfocadas en ingeniería y emprendimiento.
        2. DEBES RESPONDER EXCLUSIVAMENTE EN FORMATO JSON VÁLIDO con la siguiente estructura:
           {{
             "respuesta_guia": "Tu respuesta estratégica como XiXi",
             "emocion_detectada": "Estrategia Operativa",
             "xp_ganado": 25,
             "energia_ganada": 10
           }}

        CONTEXTO ACTUAL:
        - Nivel Usuario: {nivel_usuario}
        - Fase del Árbol: {estado_arbol}
        """

        # Invocación al modelo potente de Groq con forzado de JSON
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": mensaje_usuario},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        texto_respuesta = chat_completion.choices[0].message.content.strip()

        # Parseo seguro del contenido JSON
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
        print(f"❌ Error en Groq Cloud API: {error_detallado}")

        return {
            "respuesta_guia": f"⚠️ Diagnóstico Técnico XiXi [Groq]: {error_detallado}",
            "emocion_detectada": "Error de Red",
            "xp_ganado": 0,
            "energia_ganada": 0,
        }
