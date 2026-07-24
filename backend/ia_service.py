import os
import json
import google.generativeai as genai

# Configuración del entorno (Asegúrate de colocar tu API KEY real aquí o en tu entorno)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TU_API_KEY_AQUI")
genai.configure(api_key=GEMINI_API_KEY)


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """
    Motor de Prompt Engineering para XiXi.
    Evalúa el esfuerzo cognitivo y retorna un Modelado Lógico en JSON.
    """
    modelo = genai.GenerativeModel("gemini-pro")

    prompt_estructurado = f"""
    Actúa como 'XiXi', un tutor alienígena empático y avanzado de la plataforma EdTech 'Historias que Inspiran'.
    El usuario está en el Nivel {nivel_usuario} y la bio-estructura de su árbol es '{estado_arbol}'.
    
    Analiza este mensaje del usuario: "{mensaje_usuario}"
    
    Reglas de Gamificación y Control de Calidad:
    1. Si el usuario muestra una reflexión profunda, resolución de problemas o vulnerabilidad emocional, asigna entre 20 y 30 XP, y 10 a 15 de Energía Vital.
    2. Si el mensaje es corto, superficial o un simple saludo, asigna entre 5 y 10 XP, y 2 a 5 de Energía Vital.
    3. Tu respuesta debe ser breve (máximo 3 líneas), en tono inspirador y alienígena-amigable.
    
    RESPONDE ESTRICTAMENTE EN FORMATO JSON EXACTO. No agregues etiquetas de markdown, comillas triples ni texto antes o después de las llaves.
    Estructura requerida:
    {{
        "respuesta_guia": "Tu mensaje aquí",
        "emocion_detectada": "Emoción principal",
        "xp_ganado": 0,
        "energia_ganada": 0
    }}
    """

    try:
        respuesta = modelo.generate_content(prompt_estructurado)
        # Limpieza de sintaxis para garantizar un parsing seguro
        texto_crudo = respuesta.text.replace("```json", "").replace("```", "").strip()
        datos = json.loads(texto_crudo)
        return datos
    except Exception as e:
        # Fallback operativo en caso de latencia o error de formato de la IA
        return {
            "respuesta_guia": "👽 Frecuencia inestable. Siento tu energía, pero mis sensores requieren recalibración para procesar la experiencia completa.",
            "emocion_detectada": "interferencia",
            "xp_ganado": 5,
            "energia_ganada": 2,
        }
