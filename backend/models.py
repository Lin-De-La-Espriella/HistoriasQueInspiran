from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(String(20), default="estudiante")
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    pasaporte = relationship("Pasaporte", back_populates="dueno", uselist=False)
    arbol = relationship("ArbolProgreso", back_populates="dueno", uselist=False)
    libro_vivo = relationship("LibroVivo", back_populates="dueno", uselist=False)
    interacciones = relationship("InteraccionGuia", back_populates="dueno")
    misiones = relationship("Mision", back_populates="dueno")


class LibroVivo(Base):
    __tablename__ = "libros_vivos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    titulo_libro = Column(String(150), default="Mi Historia Inspiradora")
    paginas_completadas = Column(Integer, default=0)
    capitulo_actual = Column(Integer, default=1)
    resumen_adn = Column(JSON, default=dict)

    dueno = relationship("Usuario", back_populates="libro_vivo")


class InteraccionGuia(Base):
    __tablename__ = "interacciones_guias"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    personaje = Column(String(50), default="xixi", nullable=False)
    mensaje_usuario = Column(Text, nullable=False)
    respuesta_guia = Column(Text, nullable=False)
    fecha_interaccion = Column(DateTime(timezone=True), server_default=func.now())

    dueno = relationship("Usuario", back_populates="interacciones")


class Pasaporte(Base):
    __tablename__ = "pasaportes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    avatar_url = Column(String(255), nullable=True)
    nivel_actual = Column(Integer, default=1)
    puntos_experiencia = Column(Integer, default=0)
    insignias = Column(JSON, default=list)

    dueno = relationship("Usuario", back_populates="pasaporte")


class ArbolProgreso(Base):
    __tablename__ = "arboles_progreso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    estado_crecimiento = Column(String(50), default="semilla")
    energia_vital = Column(Integer, default=100)

    dueno = relationship("Usuario", back_populates="arbol")


class Mision(Base):
    __tablename__ = "misiones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    titulo_mision = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), default="pendiente")
    recompensa_puntos = Column(Integer, default=50)

    dueno = relationship("Usuario", back_populates="misiones")
