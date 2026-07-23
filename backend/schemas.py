from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class PasaporteBase(BaseModel):
    avatar_url: Optional[str] = None
    nivel_actual: int = 1
    puntos_experiencia: int = 0
    insignias: List[str] = []


class PasaporteRespuesta(PasaporteBase):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True


class ArbolBase(BaseModel):
    estado_crecimiento: str = "semilla"
    energia_vital: int = 100


class ArbolRespuesta(ArbolBase):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True


class MisionCrear(BaseModel):
    titulo_mision: str
    recompensa_puntos: int = 10


class MisionRespuesta(MisionCrear):
    id: int
    usuario_id: int
    estado: str

    class Config:
        from_attributes = True


class LibroVivoBase(BaseModel):
    titulo_libro: str
    paginas_completadas: int = 0
    capitulo_actual: int = 1


class LibroVivoRespuesta(LibroVivoBase):
    id: int
    usuario_id: int
    resumen_adn: dict

    class Config:
        from_attributes = True


class InteraccionCrear(BaseModel):
    personaje: str
    mensaje_usuario: str
    respuesta_guia: Optional[str] = ""


class InteraccionRespuesta(InteraccionCrear):
    id: int
    usuario_id: int
    fecha_interaccion: datetime

    class Config:
        from_attributes = True


class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
    password: str  # <-- NUEVO CAMPO AÑADIDO PARA RECIBIR LA CONTRASEÑA
    rol: Optional[str] = "estudiante"


class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool
    fecha_creacion: datetime
    pasaporte: Optional[PasaporteRespuesta] = None
    arbol: Optional[ArbolRespuesta] = None
    libro_vivo: Optional[LibroVivoRespuesta] = None

    class Config:
        from_attributes = True


# --- ESQUEMAS DE AUTENTICACIÓN ---


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
