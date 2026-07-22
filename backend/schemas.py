from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Esquema para Recibir datos al crear un usuario (Request)
class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
    rol: Optional[str] = "estudiante"


# Esquema para Devolver datos al cliente (Response)
class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True  # Permite mapear directamente desde SQLAlchemy
