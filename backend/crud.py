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
