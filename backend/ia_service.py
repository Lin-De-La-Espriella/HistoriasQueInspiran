import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str,
    estado_arbol: str,
    nivel_usuario: int,
    rol_activo: str = "emprendimiento",
) -> dict:
    """
    Motor de IA de XiXi utilizando Groq Cloud, adaptado para emprendedores infantiles y gestión de Dudi.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        return {
            "respuesta_guia": "⚠️ Error de Configuración: No se encontró la variable GROQ_API_KEY.",
            "emocion_detectada": "Configuración Requerida",
            "xp_ganado": 5,
            "energia_ganada": 2,
        }

    try:
        client = Groq(api_key=api_key)

        prompt_sistema = f"""
        Eres 'XiXi', un mentor extraterrestre neutral, sabio y lleno de luz de 'Historias que Inspiran'.
        Tu misión: Guiar a un niño/joven a CREAR SU PROPIA EMPRESA DESDE CERO.

        FASES DE SU EMPRESA SEGÚN SU ÁRBOL ({estado_arbol}):
        - Semilla/Brote Menor: Descubrir su Idea de Negocio resolviendo un problema.
        - Brote Explorador: Crear el Nombre, Logo y Colores Favoritos de su marca.
        - Árbol Joven: Escribir la Misión y Visión de su empresa de forma sencilla.
        - Árbol Frondoso: Guía Financiera (costos simples y precio de venta).
        - Árbol Cósmico: Lanzamiento y Pitch de ventas.

        DINÁMICA EMOCIONAL CRÍTICA (DUDI):
        Dudi es una nebulosa extraterrestre que representa el miedo o la duda. ¡Tener dudas NO es malo!
        Si el usuario expresa miedo, confusión o frustración:
        1. Saluda a Dudi: "¡Veo que Dudi nos acompaña! Qué bueno, eso significa que estamos aprendiendo algo nuevo."
        2. Valida: Explica que los mejores emprendedores sienten miedo, pero piden ayuda.
        3. Acción: Dale un paso ultra-sencillo para avanzar.

        DEBES RESPONDER EXCLUSIVAMENTE EN FORMATO JSON VÁLIDO:
        {{
            "respuesta_guia": "Tu respuesta inspiradora y empática",
            "emocion_detectada": "Miedo (Dudi) / Alegría / Curiosidad",
            "xp_ganado": 25,
            "energia_ganada": 10
        }}
        """

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
        return {
            "respuesta_guia": f"⚠️ Diagnóstico Técnico XiXi [Groq]: {str(e)}",
            "emocion_detectada": "Error de Red",
            "xp_ganado": 0,
            "energia_ganada": 0,
        }


def generar_mision_ia(
    estado_arbol: str, nivel_usuario: int, enfoque: str = "emprendimiento"
) -> dict:
    """
    Genera un desafío práctico para construir la empresa del niño.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return {
            "titulo_mision": "Reflexión Inicial",
            "descripcion": "Piensa en algo que te gustaría mejorar en tu entorno.",
            "recompensa_puntos": 50,
        }

    try:
        client = Groq(api_key=api_key)

        prompt_sistema = f"""
        Eres 'XiXi', mentor alienígena de niños emprendedores.
        Crea UNA misión divertida y accionable para que el niño avance en la creación de su empresa.

        Contexto:
        - Nivel: {nivel_usuario}
        - Fase (Árbol): {estado_arbol}
        - Enfoque actual: {enfoque}

        Si está en semilla: misiones sobre ideas. Si está en brote: misiones sobre logos o colores. Si es árbol joven: misión y visión.
        
        Responde ÚNICAMENTE en formato JSON VÁLIDO:
        {{
            "titulo_mision": "Título divertido (Ej: ¡Diseñando mi Logo Galáctico!)",
            "descripcion": "Instrucción clara, sencilla y motivadora.",
            "recompensa_puntos": 50
        }}
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistema},
                {
                    "role": "user",
                    "content": "Genera mi siguiente misión de emprendimiento.",
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
            "titulo_mision": "Misión de Exploración",
            "descripcion": "Dibuja cómo te imaginas tu futura empresa.",
            "recompensa_puntos": 50,
        }
    except Exception as e:
        return {
            "titulo_mision": "Dudi nos visitó",
            "descripcion": "Descansa un momento y luego intenta pedir una misión nuevamente.",
            "recompensa_puntos": 50,
        }


def generar_pagina_libro_ia(titulo_hito: str, contexto_usuario: str) -> str:
    """
    Sintetiza la experiencia como el 'Plan de Negocios' del niño.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return f"Hoy avancé en mi empresa superando: {titulo_hito}."

    try:
        client = Groq(api_key=api_key)

        prompt_sistema = """
        Eres un biógrafo infantil. Convierte el logro del niño en un párrafo inspirador (máximo 80 palabras) 
        que formará parte de su 'Libro Vivo' (su primer Plan de Negocios).
        Escribe en PRIMERA PERSONA como si el niño lo estuviera escribiendo con orgullo ("Hoy logré...", "Mi empresa está creciendo...").
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
        return f"Con el logro '{titulo_hito}', doy un paso gigante en la creación de mi empresa."
