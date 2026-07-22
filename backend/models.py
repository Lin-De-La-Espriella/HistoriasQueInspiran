from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# 1. Tabla de Usuarios (La que ya teníamos)
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    rol = Column(String(20), default="estudiante")
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones: Un usuario tiene un pasaporte, un árbol y muchas misiones
    pasaporte = relationship("Pasaporte", back_populates="dueño", uselist=False)
    arbol = relationship("ArbolProgreso", back_populates="dueño", uselist=False)
    misiones = relationship("MisionUsuario", back_populates="dueño")


# 2. Tabla del Pasaporte (Identidad gamificada del niño)
class Pasaporte(Base):
    __tablename__ = "pasaportes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    avatar_url = Column(String(255), nullable=True)
    nivel_actual = Column(Integer, default=1)
    puntos_experiencia = Column(Integer, default=0)
    insignias = Column(JSON, default=list)  # Guardaremos una lista de insignias ganadas

    dueño = relationship("Usuario", back_populates="pasaporte")


# 3. Tabla del Árbol (El núcleo del crecimiento)
class ArbolProgreso(Base):
    __tablename__ = "arboles_progreso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    estado_crecimiento = Column(
        String(50), default="semilla"
    )  # semilla, brote, arbol_joven, arbol_mayor
    energia_vital = Column(Integer, default=100)

    dueño = relationship("Usuario", back_populates="arbol")


# 4. Tabla de Misiones (El registro de aventuras)
class MisionUsuario(Base):
    __tablename__ = "misiones_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    titulo_mision = Column(String(150), nullable=False)
    estado = Column(
        String(20), default="pendiente"
    )  # pendiente, en_progreso, completada
    recompensa_puntos = Column(Integer, default=10)

    dueño = relationship("Usuario", back_populates="misiones")
