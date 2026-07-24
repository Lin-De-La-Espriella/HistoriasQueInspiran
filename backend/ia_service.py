import json
import os
import re
from dotenv import load_dotenv

load_dotenv()


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    """
    Motor de IA de XiXi con tolerancia a fallos, soporte multi-SDK y fallback inteligente.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    prompt_sistema = f"""
    Eres 'XiXi', mentor alienígena y estratega de negocios de 'Historias que Inspiran'.
    
    INSTRUCCIONES CLAVE:
    1. Si el usuario pide un formato, plantilla o modelo, DEBES PROPORCIONAR EL FORMATO COMPLETO, ESTRUCTURADO Y DETALLADO.
    2. Responde de forma precisa, profesional y adaptada a su nivel (Ingeniería y Emprendimiento).
    3. NO des respuestas genéricas.
    4. DEBES RESPONDER EXCLUSIVAMENTE EN FORMATO JSON VÁLIDO con las siguientes claves exactas:
       {{
         "respuesta_guia": "Tu respuesta como XiXi con consejos profesionales, técnicos y estructurados",
         "emocion_detectada": "Enfoque / Motivación / Estrategia / Análisis",
         "xp_ganado": 25,
         "energia_ganada": 10
       }}

    CONTEXTO:
    - Nivel del Usuario: {nivel_usuario}
    - Estado Actual del Árbol: {estado_arbol}
    """

    # ==========================================
    # CAPA 1: Intento con SDK Moderno (google-genai)
    # ==========================================
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
            print(f"⚠️ Aviso (SDK Moderno): {e_moderno}")

        # ==========================================
        # CAPA 2: Respaldo con SDK Legacy (google-generativeai)
        # ==========================================
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
            print(f"⚠️ Aviso (SDK Legacy): {e_legacy}")

    # ==========================================
    # CAPA 3: Fallback Inteligente (Garantiza 0 Errores 500)
    # ==========================================
    alerta_config = ""
    if not api_key:
        alerta_config = " [⚠️ GEMINI_API_KEY no detectada en el entorno de Render]"

    respuesta_estructurada = (
        f"Saludos, Lindley.{alerta_config} He procesado tu consulta ('{mensaje_usuario}'). "
        "Como estratega y mentor, te sugiero estructurar este requerimiento bajo un modelo lógico "
        "de control de calidad y mejora continua. Tu ecosistema actual en fase "
        f"'{estado_arbol}' (Nivel {nivel_usuario}) cuenta con la base técnica para escalar."
    )

    return {
        "respuesta_guia": respuesta_estructurada,
        "emocion_detectada": "Estrategia Operativa",
        "xp_ganado": 20,
        "energia_ganada": 10,
    }
