"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / API
Esquemas de Validación y Serialización Pydantic
===============================================================================
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict


# -----------------------------------------------------------------------------
# Autenticación y Usuario
# -----------------------------------------------------------------------------
class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    rol: str
    activo: bool


# -----------------------------------------------------------------------------
# Componentes del Creador
# -----------------------------------------------------------------------------
class PasaporteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    avatar_url: str
    nivel_actual: int
    puntos_experiencia: int
    insignias: List[Dict[str, Any]]


class ArbolProgresoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    estado_crecimiento: str
    energia_vital: int


class LibroVivoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    titulo_libro: str
    capitulo_actual: int
    paginas_completadas: int
    capitulos_narrativos: List[Dict[str, Any]]
    resumen_adn: Dict[str, Any]


class MisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo_mision: str
    descripcion: str
    estado: str
    recompensa_puntos: int


# -----------------------------------------------------------------------------
# Solicitud y Respuesta de IA (Motor Gemini / OpenAI)
# -----------------------------------------------------------------------------
class GenerarHistoriaRequest(BaseModel):
    capitulo: int
    respuestas_usuario: Dict[str, Any]


class GenerarHistoriaResponse(BaseModel):
    capitulo: int
    historia_narrativa: str
    mision_sugerida: str
    puntos_otorgados: int = 50


class MensajeChat(BaseModel):
    personaje: str
    mensaje: str


class ValidarMisionRequest(BaseModel):
    mision: str
    respuesta_usuario: str


class ValidarMisionResponse(BaseModel):
    cumplida: bool
    feedback: str
    puntos_otorgados: int = 30
