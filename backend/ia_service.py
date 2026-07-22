import os
from google import genai
from config import GEMINI_API_KEY

# Inicializar el cliente oficial de Google GenAI
client = genai.Client(api_key=GEMINI_API_KEY)


def generar_respuesta_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> str:
    """
    Genera la respuesta de XiXi utilizando el modelo gratuito Gemini 2.5 Flash.
    """

    system_prompt = f"""
    Eres XiXi, una guía mágica, sabia y amigable en la plataforma educativa 'Historias que Inspiran'.
    Tu objetivo es motivar al estudiante a explorar, aprender y desarrollar su inteligencia emocional.
    
    Contexto del estudiante:
    - Nivel actual en su Pasaporte: Nivel {nivel_usuario}
    - Estado de su Árbol de Progreso: {estado_arbol}
    
    Reglas estrictas de respuesta:
    1. Mantén un tono cálido, empático, protector y alentador.
    2. Haz al menos una referencia sutil al estado de su árbol ('{estado_arbol}') o a su nivel para que sienta que su progreso es real.
    3. Entrega respuestas concisas y estructuradas (máximo 3 párrafos cortos).
    4. Termina siempre con una pregunta abierta para fomentar la curiosidad.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nMensaje del estudiante: {mensaje_usuario}",
        )
        return response.text

    except Exception as e:
        return f"Hmm, mis poderes mágicos están recargándose en este momento. Dame un segundo y volvamos a intentarlo. (Error interno: {str(e)})"
