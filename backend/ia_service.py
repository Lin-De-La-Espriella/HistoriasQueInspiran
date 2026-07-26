import random
from typing import Dict, Any

# ==========================================
# 1. BASES DE CONOCIMIENTO (DICCIONARIOS)
# ==========================================

EMOCIONES: Dict[str, list] = {
    "feliz": ["feliz", "emocionado", "contento", "genial", "increíble", "maravilloso"],
    "triste": ["triste", "solo", "llorar", "mal", "desanimado"],
    "miedo": ["miedo", "asustado", "nervioso", "ansiedad", "duda"],
    "frustrado": ["no puedo", "difícil", "imposible", "me rindo", "bloqueado"],
    "creativo": ["idea", "dibujar", "crear", "inventar", "imaginar"],
}

RESPUESTAS_XIXI: Dict[str, list] = {
    "feliz": [
        "¡Eso me encanta!",
        "¡Qué energía tan bonita!",
        "Hoy tu árbol creció un poquito más.",
    ],
    "triste": [
        "No pasa nada si hoy fue difícil.",
        "Los árboles también necesitan lluvia para crecer.",
        "Estoy contigo, paso a paso.",
    ],
    "miedo": [
        "El miedo aparece cuando estamos creciendo.",
        "Respira... seguimos juntos.",
        "Cada héroe sintió miedo alguna vez. ¡Tú puedes!",
    ],
    "frustrado": [
        "No necesitas hacerlo perfecto.",
        "Solo da el siguiente paso. Yo te ayudo.",
        "Confío en ti. Tomemos un respiro y sigamos.",
    ],
    "creativo": [
        "¡Eso suena increíble!",
        "Quiero conocer esa idea a fondo.",
        "¡Genial! Vamos a convertirla en un proyecto real.",
    ],
    "neutral": [
        "Cuéntame más, te leo.",
        "Estoy escuchando con mucha atención.",
        "Eso parece muy interesante para tu empresa.",
    ],
}

XP: Dict[str, int] = {
    "feliz": 10,
    "creativo": 15,
    "neutral": 5,
    "triste": 8,
    "frustrado": 12,
    "miedo": 12,
}

ENERGIA: Dict[str, int] = {
    "feliz": 5,
    "creativo": 7,
    "neutral": 2,
    "triste": 3,
    "frustrado": 4,
    "miedo": 4,
}

MISIONES: Dict[int, list] = {
    1: [
        (
            "Dibuja tu sueño",
            "Dibuja en un papel cómo imaginas tu empresa en el futuro.",
            25,
        ),
        (
            "Pregunta a tu alrededor",
            "Descubre qué problema tienen 3 personas cercanas a ti.",
            30,
        ),
        ("Lluvia de ideas", "Escribe 3 nombres divertidos para tu futura empresa.", 25),
    ],
    2: [
        (
            "Diseña tu logo",
            "Crea tres bocetos diferentes para el logo de tu marca.",
            40,
        ),
        (
            "Tus Colores",
            "Elige los 2 colores que representarán la energía de tu marca.",
            35,
        ),
    ],
    3: [
        (
            "Construye un prototipo",
            "Haz la primera versión de tu producto con materiales reciclados.",
            50,
        ),
        (
            "Tu primer discurso",
            "Escribe en 2 líneas qué hace tu empresa y léelo en voz alta.",
            45,
        ),
    ],
    4: [
        (
            "Calcula tus costos",
            "Haz una lista de lo que necesitas comprar para crear 1 producto.",
            60,
        ),
        (
            "Precio Estrella",
            "Define a qué precio venderás tu creación para tener ganancia.",
            60,
        ),
    ],
}

# ==========================================
# 2. MOTOR DE PROCESAMIENTO
# ==========================================


def detectar_emocion(texto: str) -> str:
    """Escanea el texto del niño y retorna la emoción predominante."""
    texto_limpio = texto.lower()
    for emocion, palabras in EMOCIONES.items():
        for palabra in palabras:
            if palabra in texto_limpio:
                return emocion
    return "neutral"


def respuesta_xixi(emocion: str) -> str:
    """Selecciona una respuesta empática basada en la emoción."""
    return random.choice(RESPUESTAS_XIXI.get(emocion, RESPUESTAS_XIXI["neutral"]))


def generar_analisis_xixi(
    mensaje_usuario: str,
    estado_arbol: str,
    nivel_usuario: int,
    rol_activo: str = "emprendimiento",
) -> Dict[str, Any]:
    """Cerebro principal que procesa la interacción del niño con XiXi."""
    emocion = detectar_emocion(mensaje_usuario)
    respuesta = respuesta_xixi(emocion)

    # Dudi interviene sutilmente si hay emociones de bloqueo
    if emocion in ["miedo", "frustrado", "triste"]:
        respuesta = (
            f"☁️ Dudi está por aquí, y eso está bien. 👽 XiXi dice: '{respuesta}'"
        )
    else:
        respuesta = f"👽 XiXi dice: '{respuesta}'"

    return {
        "respuesta_guia": respuesta,
        "emocion_detectada": emocion,
        "xp_ganado": XP.get(emocion, 5),
        "energia_ganada": ENERGIA.get(emocion, 2),
        "estado_arbol": estado_arbol,
        "nivel": nivel_usuario,
        "rol": rol_activo,
    }


def generar_mision_ia(
    estado_arbol: str, nivel_usuario: int, enfoque: str = "emprendimiento"
) -> Dict[str, Any]:
    """Generador predictivo de misiones basado en el nivel del niño."""
    # Aseguramos que el nivel no exceda las llaves disponibles en el diccionario
    nivel = min(nivel_usuario, max(MISIONES.keys()))

    titulo, descripcion, xp_mision = random.choice(MISIONES[nivel])

    return {
        "titulo_mision": titulo,
        "descripcion": descripcion,
        "recompensa_puntos": xp_mision,
    }


def generar_pagina_libro_ia(titulo_hito: str, contexto_usuario: str) -> str:
    """
    Sintetiza la experiencia completada para el 'Libro Vivo'.
    (Mantiene la compatibilidad con main.py)
    """
    return f"Hoy logré un avance increíble: '{titulo_hito}'. Cada día mi empresa toma más forma."
