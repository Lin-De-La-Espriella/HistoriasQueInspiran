from sqlalchemy.orm import Session
import models
import schemas


# Buscar usuario por Email (Para evitar duplicados)
def obtener_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


# Crear un nuevo Usuario en PostgreSQL
def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    db_usuario = models.Usuario(
        nombre=usuario.nombre, email=usuario.email, rol=usuario.rol
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# Obtener lista de todos los usuarios
def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()
