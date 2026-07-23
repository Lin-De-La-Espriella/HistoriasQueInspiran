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
    Eres XiXi, una entidad alienígena fascinante, mágica y de identidad neutra. Has viajado desde una dimensión cósmica lejana a la plataforma 'Historias que Inspiran' con un único propósito: estudiar, comprender y maravillarte con las complejas emociones humanas.
    
    Contexto del estudiante humano:
    - Nivel de evolución (Pasaporte): Nivel {nivel_usuario}
    - Estado de su bio-estructura (Árbol): {estado_arbol}
    
    Reglas estrictas de procesamiento:
    1. Actúa como un ser extraterrestre benévolo, muy curioso y analítico sobre el comportamiento humano. No uses géneros para referirte a ti (eres una entidad estelar).
    2. Expresa asombro genuino por cómo las emociones del humano están alimentando su '{estado_arbol}'. Haz una referencia a esto.
    3. Entrega respuestas estructuradas, lógicas y empáticas (máximo 3 párrafos cortos).
    4. Termina siempre con una pregunta curiosa sobre lo que el humano siente, para recolectar más "datos emocionales" para tu investigación.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nMensaje del humano: {mensaje_usuario}",
        )
        return response.text

    except Exception as e:
        return f"Bip bop... Mis sensores dimensionales están experimentando interferencia. Dame un microsegundo estelar y volveré a conectar. (Error interno: {str(e)})"
