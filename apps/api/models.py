"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / API
Modelos ORM de Base de Datos (SQLAlchemy)
===============================================================================
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(String(20), default="estudiante")
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    pasaporte = relationship(
        "Pasaporte", back_populates="dueño", uselist=False, cascade="all, delete-orphan"
    )
    arbol = relationship(
        "ArbolProgreso",
        back_populates="dueño",
        uselist=False,
        cascade="all, delete-orphan",
    )
    # CORRECCIÓN: Se cambió back_populates="dueño" a "usuario" para alinear con la clase LibroVivo
    libro_vivo = relationship(
        "LibroVivo",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    misiones = relationship(
        "Mision", back_populates="dueño", cascade="all, delete-orphan"
    )


class Pasaporte(Base):
    __tablename__ = "pasaportes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    avatar_url = Column(String(255), default="👦 Rafa")
    nivel_actual = Column(Integer, default=1)
    puntos_experiencia = Column(Integer, default=0)
    insignias = Column(JSON, default=list)

    dueño = relationship("Usuario", back_populates="pasaporte")


class ArbolProgreso(Base):
    __tablename__ = "arboles_progreso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    estado_crecimiento = Column(String(50), default="semilla")
    energia_vital = Column(Integer, default=100)

    dueño = relationship("Usuario", back_populates="arbol")


class LibroVivo(Base):
    __tablename__ = "libros_vivos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    titulo_libro = Column(String, default="Mi Libro de Aventuras")
    capitulo_actual = Column(Integer, default=1)
    paginas_completadas = Column(Integer, default=0)
    capitulos_narrativos = Column(JSON, default=list)
    resumen_adn = Column(JSON, default=dict)

    # El espejo perfecto que ahora coincide con Usuario.libro_vivo
    usuario = relationship("Usuario", back_populates="libro_vivo")


class Mision(Base):
    __tablename__ = "misiones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    titulo_mision = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), default="pendiente")
    recompensa_puntos = Column(Integer, default=50)

    dueño = relationship("Usuario", back_populates="misiones")
