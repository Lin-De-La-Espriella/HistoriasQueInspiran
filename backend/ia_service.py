import json
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carga explicita de variables de entorno desde la raíz y carpeta backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))


def obtener_cliente_gemini():
    """Instancia el cliente oficial usando el nuevo SDK google-genai."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key and api_key != "tu_clave_aqui":
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            print(f"❌ Error al instanciar genai.Client: {e}")
            return None
    return None


def generar_analisis_xixi(
    mensaje_usuario: str, estado_arbol: str, nivel_usuario: int
) -> dict:
    client = obtener_cliente_gemini()

    if not client:
        print(
            "⚠️ ALERTA: No se pudo obtener el cliente Gemini. Entrando a respuesta local."
        )
        return _respuesta_heuristica_avanzada(mensaje_usuario)

    try:
        system_instruction = f"""
        Eres 'XiXi', mentor psico-pedagógico y estratega de negocios alienígena de 'Historias que Inspiran'.
        
        INSTRUCCIONES CLAVE DE RESPUESTA:
        1. Analiza con precisión la intención del usuario. Si pide un plan de trabajo, cronograma o estrategia para su empresa, proporciónale PASOS CONCRETOS, ESTRUCTURADOS Y EJECUTABLES para HOY.
        2. Mantén un tono profesional, inspirador y directo, combinando perspectiva de negocios con tu toque alienígena.
        3. NO des respuestas genéricas ni evasivas.
        
        CONTEXTO TÉCNICO:
        - Nivel de Evolución del Usuario: {nivel_usuario}
        - Estado del Árbol de Crecimiento: {estado_arbol}
        """

        prompt = f'El usuario dice: "{mensaje_usuario}"'

        # Configuración nativa del SDK moderno
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "respuesta_guia": {"type": "STRING"},
                    "emocion_detectada": {"type": "STRING"},
                    "xp_ganado": {"type": "INTEGER"},
                    "energia_ganada": {"type": "INTEGER"},
                },
                "required": [
                    "respuesta_guia",
                    "emocion_detectada",
                    "xp_ganado",
                    "energia_ganada",
                ],
            },
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"❌ ERROR EXACTO EN LLAMADA A GEMINI: {e}")
        return _respuesta_heuristica_avanzada(mensaje_usuario)


def _respuesta_heuristica_avanzada(mensaje: str) -> dict:
    return {
        "respuesta_guia": f"👽 [Respuesta Local] Mensaje recibido: '{mensaje}'. (Verifica la terminal de Uvicorn para ver el error de la API).",
        "emocion_detectada": "Contingencia",
        "xp_ganado": 5,
        "energia_ganada": 2,
    }
