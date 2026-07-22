from sqlalchemy.orm import Session
import models
import schemas


# Obtener usuario por Email
def obtener_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


# Crear Usuario + Inicializar Pasaporte y Árbol de forma atómica
def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    # 1. Crear el registro del usuario
    db_usuario = models.Usuario(
        nombre=usuario.nombre, email=usuario.email, rol=usuario.rol
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    # 2. Inicializar su Pasaporte
    db_pasaporte = models.Pasaporte(usuario_id=db_usuario.id)
    db.add(db_pasaporte)

    # 3. Inicializar su Árbol de Crecimiento
    db_arbol = models.ArbolProgreso(usuario_id=db_usuario.id)
    db.add(db_arbol)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# Listar todos los usuarios
def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()


# Crear Misión para un Usuario
def crear_mision_usuario(db: Session, mision: schemas.MisionCrear, usuario_id: int):
    db_mision = models.MisionUsuario(
        usuario_id=usuario_id,
        titulo_mision=mision.titulo_mision,
        recompensa_puntos=mision.recompensa_puntos,
    )
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    return db_mision


# Obtener Misiones de un Usuario
def obtener_misiones_usuario(db: Session, usuario_id: int):
    return (
        db.query(models.MisionUsuario)
        .filter(models.MisionUsuario.usuario_id == usuario_id)
        .all()
    )


# --- MOTOR DE GAMIFICACIÓN: Completar Misión ---
def completar_mision(db: Session, usuario_id: int, mision_id: int):
    # 1. Buscar la misión y verificar que pertenece al usuario
    db_mision = (
        db.query(models.MisionUsuario)
        .filter(
            models.MisionUsuario.id == mision_id,
            models.MisionUsuario.usuario_id == usuario_id,
        )
        .first()
    )

    # Validar que exista y no esté ya completada para evitar duplicidad de puntos
    if not db_mision or db_mision.estado == "completada":
        return None

    # 2. Cambiar estado
    db_mision.estado = "completada"
    puntos = db_mision.recompensa_puntos

    # 3. Transferir recursos al Pasaporte
    db_pasaporte = (
        db.query(models.Pasaporte)
        .filter(models.Pasaporte.usuario_id == usuario_id)
        .first()
    )
    if db_pasaporte:
        db_pasaporte.puntos_experiencia += puntos
        # Fórmula de Nivel: Cada 100 puntos sube 1 nivel
        db_pasaporte.nivel_actual = (db_pasaporte.puntos_experiencia // 100) + 1

    # 4. Transferir recursos al Árbol y calcular Evolución
    db_arbol = (
        db.query(models.ArbolProgreso)
        .filter(models.ArbolProgreso.usuario_id == usuario_id)
        .first()
    )
    if db_arbol:
        db_arbol.energia_vital += puntos

        # Lógica de Evolución
        if db_arbol.energia_vital >= 200:
            db_arbol.estado_crecimiento = "arbol_joven"
        elif db_arbol.energia_vital >= 150:
            db_arbol.estado_crecimiento = "brote"

    # 5. Sellar la transacción en la base de datos
    db.commit()
    db.refresh(db_mision)
    return db_mision
