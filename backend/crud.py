# Importación de módulos locales con ruta relativa (.)
import models
import schemas
import security

# Importación de librerías externas
from sqlalchemy.orm import Session


def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    # 1. Encriptar contraseña
    hashed_pw = security.obtener_password_hash(usuario.password)

    # 2. Crear instancia del usuario
    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        hashed_password=hashed_pw,
        rol=usuario.rol,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    # 3. Inicializar Ecosistema (Usando los nombres exactos de models.py)
    db_pasaporte = models.Pasaporte(usuario_id=db_usuario.id)

    # Manejo dinámico según el nombre de la clase en tu models.py (Arbol o ArbolProgreso)
    if hasattr(models, "ArbolProgreso"):
        db_arbol = models.ArbolProgreso(usuario_id=db_usuario.id)
    else:
        db_arbol = models.Arbol(usuario_id=db_usuario.id)

    db_libro = models.LibroVivo(usuario_id=db_usuario.id)

    # 4. Inserción agrupada en la BD
    db.add_all([db_pasaporte, db_arbol, db_libro])
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def obtener_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def obtener_libro_vivo(db: Session, usuario_id: int):
    return (
        db.query(models.LibroVivo)
        .filter(models.LibroVivo.usuario_id == usuario_id)
        .first()
    )


def registrar_interaccion(
    db: Session, usuario_id: int, interaccion: schemas.InteraccionCrear
):
    db_interaccion = models.InteraccionGuia(
        usuario_id=usuario_id,
        personaje=interaccion.personaje,
        mensaje_usuario=interaccion.mensaje_usuario,
        respuesta_guia=interaccion.respuesta_guia,
    )
    db.add(db_interaccion)
    db.commit()
    db.refresh(db_interaccion)
    return db_interaccion


def obtener_historial_interacciones(db: Session, usuario_id: int):
    return (
        db.query(models.InteraccionGuia)
        .filter(models.InteraccionGuia.usuario_id == usuario_id)
        .all()
    )


def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()


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


def obtener_misiones_usuario(db: Session, usuario_id: int):
    return (
        db.query(models.MisionUsuario)
        .filter(models.MisionUsuario.usuario_id == usuario_id)
        .all()
    )


def completar_mision(db: Session, usuario_id: int, mision_id: int):
    db_mision = (
        db.query(models.MisionUsuario)
        .filter(
            models.MisionUsuario.id == mision_id,
            models.MisionUsuario.usuario_id == usuario_id,
        )
        .first()
    )

    if not db_mision or db_mision.estado == "completada":
        return None

    db_mision.estado = "completada"
    puntos = db_mision.recompensa_puntos

    db_pasaporte = (
        db.query(models.Pasaporte)
        .filter(models.Pasaporte.usuario_id == usuario_id)
        .first()
    )
    if db_pasaporte:
        db_pasaporte.puntos_experiencia += puntos
        db_pasaporte.nivel_actual = (db_pasaporte.puntos_experiencia // 100) + 1

    db_arbol = (
        db.query(models.ArbolProgreso)
        .filter(models.ArbolProgreso.usuario_id == usuario_id)
        .first()
    )
    if db_arbol:
        db_arbol.energia_vital += puntos

        if db_arbol.energia_vital >= 200:
            db_arbol.estado_crecimiento = "arbol_joven"
        elif db_arbol.energia_vital >= 150:
            db_arbol.estado_crecimiento = "brote"

    db.commit()
    db.refresh(db_mision)
    return db_mision
