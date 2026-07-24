import json
import os
import re
from dotenv import load_dotenv

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """
    Motor de IA de XiXi con registro de errores detallado para diagnóstico en Render.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        print(
            "❌ ALERTA CRÍTICA: La variable GEMINI_API_KEY está vacía o no existe en el entorno."
        )

    prompt_sistema = f"""
    Eres 'XiXi', mentor alienígena y estratega de negocios de 'Historias que Inspiran'.
    
    INSTRUCCIONES CLAVE:
    1. Si el usuario pide un formato o guía, proveylo detalladamente y de forma estructurada.
    2. Responde con un tono profesional, adaptado a ingeniería y emprendimiento.
    3. DEBES RESPONDER EXCLUSIVAMENTE EN FORMATO JSON VÁLIDO con las siguientes claves:
       {{
         "respuesta_guia": "Tu respuesta detallada y profesional como XiXi",
         "emocion_detectada": "Estrategia Operativa",
         "xp_ganado": 25,
         "energia_ganada": 10
       }}

    CONTEXTO:
    - Nivel del Usuario: {nivel_usuario}
    - Estado Actual del Árbol: {estado_arbol}
    """

    # Intento con SDK Moderno (google-genai)
    if api_key:
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
                model="gemini-2.0-flash",
                contents=f'Genera la respuesta para: "{mensaje_usuario}"',
                config=config,
            )
            if response and response.text:
                return json.loads(response.text)
        except Exception as e_moderno:
            print(f"❌ ERROR DETALLADO EN GEMINI (SDK Moderno): {str(e_moderno)}")

        # Respaldo con SDK Legacy (google-generativeai)
        try:
            import google.generativeai as legacy_genai

            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")

            raw_response = model.generate_content(
                f"{prompt_sistema}\n\nResponde estrictamente en JSON a: {mensaje_usuario}"
            )
            texto = raw_response.text.strip()
            match = re.search(r"\{.*\}", texto, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e_legacy:
            print(f"❌ ERROR DETALLADO EN GEMINI (SDK Legacy): {str(e_legacy)}")

    # Fallback si todo falla (permite ver el error exacto en los logs)
    return {
        "respuesta_guia": f"[Modo de Diagnóstico Activo] XiXi no pudo conectar con Gemini. Revisa los logs de Render para ver el error exacto de la API Key o la red.",
        "emocion_detectada": "Anomalía de Red",
        "xp_ganado": 10,
        "energia_ganada": 5,
    }
