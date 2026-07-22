from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# --- ESQUEMAS DE PASAPORTE ---
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


# --- ESQUEMAS DE ÁRBOL ---
class ArbolBase(BaseModel):
    estado_crecimiento: str = "semilla"
    energia_vital: int = 100


class ArbolRespuesta(ArbolBase):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True


# --- ESQUEMAS DE MISIÓNS ---
class MisionCrear(BaseModel):
    titulo_mision: str
    recompensa_puntos: int = 10


class MisionRespuesta(MisionCrear):
    id: int
    usuario_id: int
    estado: str

    class Config:
        from_attributes = True


# --- ESQUEMAS DE USUARIO ---
class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
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

    class Config:
        from_attributes = True
