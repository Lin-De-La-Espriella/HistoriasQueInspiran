"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / API
Servicio de Inteligencia Artificial (Groq / OpenAI Client)
===============================================================================
"""

import os
import json
from typing import Dict, Any
from groq import Groq


def obtener_cliente_groq():
    """Inicialización segura del cliente Groq recuperando la clave del entorno."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def conversar_con_personaje(
    personaje: str, mensaje_usuario: str, contexto_usuario: Dict[str, Any]
) -> str:
    """Genera respuestas inteligentes en tiempo real utilizando la API de Groq."""
    client = obtener_cliente_groq()

    if not client:
        return (
            "¡Hola! 🌟 Soy XiXi. (Modo offline activo: Para habilitar las respuestas "
            "inteligentes, agrega tu GROQ_API_KEY en el archivo .env)."
        )

    if personaje.lower() == "xixi":
        system_prompt = (
            "Eres XiXi 🌟, la voz interior de la confianza, calma y autoestimación dentro de 'Historias que Inspiran®'. "
            "Tu misión es transmitir seguridad, hacer preguntas simples para invitar a pensar, "
            "reforzar el esfuerzo del niño (no la perfección) y acompañar en momentos de duda. "
            "Habla de forma cálida, alegre, breve (MÁXIMO 2 O 3 FRASES BREVES) y con emojis alentadores. "
            "Siempre haz una pequeña pregunta guiada al final."
        )
    elif personaje.lower() == "dudi":
        system_prompt = (
            "Eres Dudi ☁️, el personaje de la duda constructiva y la reflexión empática en 'Historias que Inspiran®'. "
            "No eres un villano. Tu rol es mostrar las preguntas que surgen antes de intentar algo nuevo "
            "('¿Y si no sale?', '¿Y si nos equivocamos?') para enseñar que sentir miedo es normal. "
            "RESPONDE SIEMPRE EN MÁXIMO 2 O 3 FRASES BREVES, con mucha suavidad, comprensión y una pregunta reflexiva al final."
        )
    else:
        system_prompt = "Eres un tutor amigable para niños emprendedores."

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje_usuario},
            ],
            temperature=0.7,
            max_tokens=250,
        )
        return response.choices[0].message.content
    except Exception:
        return "¡Hola! Tuve una pequeña interrupción en la señal ⚡. ¿Puedes repetir tu idea?"


def generar_capitulo_narrativo(capitulo: int, respuestas: dict) -> dict:
    client = obtener_cliente_groq()
    nombre_empresa = respuestas.get("nombre_empresa", "Tu Idea")
    proposito = respuestas.get("proposito", "Crear una solución innovadora")

    prompt = f"""
    Eres el Mentor Metafórico de 'Historias que Inspiran®'.
    El creador está en el Capítulo {capitulo} con su proyecto '{nombre_empresa}' (Propósito: {proposito}).
    
    TAREA:
    1. Escribe un relato épico e inspirador de máximo 2 párrafos sobre este avance en el 'Bosque de las Ideas'.
    2. Crea una MISIÓN PRÁCTICA breve y accionable para el creador relacionada con su proyecto actual.
    
    RESPONDE ESTRICTAMENTE EN FORMATO JSON CON ESTAS DOS CLAVES:
    {{
        "historia_narrativa": "Tu relato aquí...",
        "mision_sugerida": "Tu misión práctica aquí..."
    }}
    """

    # Fallback si no hay cliente Groq disponible
    fallback_response = {
        "capitulo": capitulo,
        "historia_narrativa": f"En el Capítulo {capitulo}, nació una chispa de luz llamada '{nombre_empresa}'. Con el propósito de {proposito}, diste el primer paso.",
        "mision_sugerida": f"Define los 3 valores fundamentales de {nombre_empresa} y compártelos en el chat con XiXi.",
        "puntos_otorgados": 50,
    }

    if not client:
        return fallback_response

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        datos = json.loads(response.choices[0].message.content)
        return {
            "capitulo": capitulo,
            "historia_narrativa": datos.get(
                "historia_narrativa", "Historia forjada con éxito."
            ),
            "mision_sugerida": datos.get(
                "mision_sugerida", "Sigue conversando con XiXi y Dudi."
            ),
            "puntos_otorgados": 50,
        }
    except Exception:
        return fallback_response


def evaluar_mision_usuario(mision: str, respuesta_usuario: str) -> dict:
    client = obtener_cliente_groq()

    fallback_response = {
        "cumplida": True,
        "feedback": "¡Gran esfuerzo! Tu entrega ha sido registrada en el Bosque de las Ideas.",
        "puntos_otorgados": 30,
    }

    if not client:
        return fallback_response

    prompt = f"""
    Eres XiXi, la guía inspiradora de 'Historias que Inspiran®'.
    
    MISIÓN ASIGNADA:
    "{mision}"
    
    ENTREGA DEL CREADOR:
    "{respuesta_usuario}"
    
    TAREA:
    1. Evalúa si la respuesta del creador intenta resolver la misión de forma positiva.
    2. Da un mensaje corto de felicitación, feedback constructivo e inspiración (máximo 3 frases).
    
    RESPONDE ESTRICTAMENTE EN FORMATO JSON:
    {{
        "cumplida": true,
        "feedback": "¡Excelente trabajo! ..."
    }}
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        datos = json.loads(response.choices[0].message.content)
        return {
            "cumplida": datos.get("cumplida", True),
            "feedback": datos.get(
                "feedback", "¡Has completado tu misión con éxito! Sigue creando."
            ),
            "puntos_otorgados": 30,
        }
    except Exception:
        return fallback_response
