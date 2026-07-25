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


def generar_mision_ia(estado_arbol: str, nivel_usuario: int) -> dict:
    """
    Genera un desafío personalizado utilizando Groq Cloud en función
    del nivel y la fase de la bio-estructura del usuario.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return {
            "titulo_mision": "Reflexión Operativa",
            "descripcion": "Establece tu meta principal para este sprint de desarrollo.",
            "recompensa_puntos": 50,
        }

    try:
        client = Groq(api_key=api_key)

        prompt_sistema = f"""
        Eres 'XiXi', mentor alienígena y estratega de 'Historias que Inspiran'.
        Diseña una misión práctica, reflexiva y estratégica para el usuario.

        CONTEXTO DEL USUARIO:
        - Nivel Actual: {nivel_usuario}
        - Fase de Bio-Estructura (Árbol): {estado_arbol}

        REGLAS STRICTAS DE RESPUESTA:
        Responde ÚNICAMENTE en formato JSON VÁLIDO con esta estructura:
        {{
            "titulo_mision": "Título corto y potente (Ej: Optimización de Procesos)",
            "descripcion": "Acción concreta orientada a ingeniería, liderazgo o emprendimiento.",
            "recompensa_puntos": 50
        }}
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {
                    "role": "user",
                    "content": "Genera mi siguiente misión de evolución personalizada.",
                },
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        respuesta = chat_completion.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", respuesta, re.DOTALL)
        if match:
            return json.loads(match.group(0))

        return {
            "titulo_mision": "Análisis de Resiliencia",
            "descripcion": "Documenta una lección clave aprendida en tu proyecto.",
            "recompensa_puntos": 50,
        }
    except Exception as e:
        print(f"❌ Error al generar misión dinámicamente: {e}")
        return {
            "titulo_mision": "Sincronización de Enfoque",
            "descripcion": "Define el entregable clave de tu jornada.",
            "recompensa_puntos": 50,
        }


def generar_pagina_libro_ia(titulo_hito: str, contexto_usuario: str) -> str:
    """
    Sintetiza la experiencia y reflexiones del usuario en una página
    narrativa e inspiradora para su 'Libro Vivo'.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return (
            f"Hoy superé un gran desafío: {titulo_hito}. Un paso firme en mi historia."
        )

    try:
        client = Groq(api_key=api_key)

        prompt_sistema = """
        Eres un biógrafo experto y mentor de liderazgo. Tu tarea es tomar un logro u objetivo completado 
        por el usuario y convertirlo en un párrafo reflexivo, motivador e inspirador (máximo 80 palabras).
        Escribe siempre en PRIMERA PERSONA ("Hoy comprendí...", "Al superar este reto...").
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {
                    "role": "user",
                    "content": f"El logro completado fue: '{titulo_hito}'. Contexto extra: '{contexto_usuario}'. Escribe mi página de diario.",
                },
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )

        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error al redactar página del Libro Vivo: {e}")
        return f"Con el logro '{titulo_hito}', marco un hito clave en mi camino de evolución personal e ingenieril."
