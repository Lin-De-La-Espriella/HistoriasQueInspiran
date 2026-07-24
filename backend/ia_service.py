import json
import os
import re
from dotenv import load_dotenv

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        print("❌ CRÍTICO: GEMINI_API_KEY no está configurada en Render.")
        return {
            "respuesta_guia": "👽 [Error de Configuración] La variable GEMINI_API_KEY no se encuentra cargada en el servidor de Render. Por favor agrégala en la pestaña Environment de tu Web Service.",
            "emocion_detectada": "Configuración Requerida",
            "xp_ganado": 0,
            "energia_ganada": 0,
        }

    prompt_sistema = f"""
    Eres 'XiXi', mentor alienígena y estratega de negocios de 'Historias que Inspiran'.
    
    INSTRUCCIONES CLAVE:
    1. Si el usuario pide un formato, plantilla o modelo, DEBES PROPORCIONAR EL FORMATO COMPLETO, ESTRUCTURADO Y DETALLADO.
    2. Responde de forma precisa, profesional y adaptada a su nivel.
    3. NO des respuestas genéricas.

    CONTEXTO:
    - Nivel: {nivel_usuario}
    - Estado Árbol: {estado_arbol}
    - Consulta del Usuario: "{mensaje_usuario}"

    FORMATO DE SALIDA (SOLO JSON):
    {{
        "respuesta_guia": "Escribe aquí la respuesta completa o formato solicitado...",
        "emocion_detectada": "Enfoque Estratégico",
        "xp_ganado": 25,
        "energia_ganada": 10
    }}
    """

    # Intento con SDK google-genai
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=prompt_sistema,
            temperature=0.7,
            response_mime_type="application/json",
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f'Genera la respuesta para: "{mensaje_usuario}"',
            config=config,
        )
        return json.loads(response.text)

    except Exception as e_moderno:
        print(f"⚠️ Falló SDK google-genai: {e_moderno}")

    # Intento de respaldo con google-generativeai
    try:
        import google.generativeai as legacy_genai

        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel("gemini-1.5-flash")

        raw_response = model.generate_content(
            f"{prompt_sistema}\n\nResponde a: {mensaje_usuario}"
        )
        texto = raw_response.text.strip()

        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            return {
                "respuesta_guia": texto,
                "emocion_detectada": "Estrategia",
                "xp_ganado": 20,
                "energia_ganada": 8,
            }

    except Exception as e_legacy:
        print(f"❌ ERROR EN GEMINI API: {e_legacy}")
        return {
            "respuesta_guia": f"👽 [Error API Render]: {str(e_legacy)}",
            "emocion_detectada": "Error de Conexión",
            "xp_ganado": 0,
            "energia_ganada": 0,
        }
