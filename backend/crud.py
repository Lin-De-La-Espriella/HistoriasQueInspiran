from backend import models, schemas, security
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def obtener_usuario_por_email(db: Session, email: str):
    """Busca y retorna un usuario por su dirección de correo electrónico."""
    return (
        db.query(models.Usuario)
        .filter(models.Usuario.email == email.strip().lower())
        .first()
    )


def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    """Retorna una lista paginada de usuarios registrados."""
    return db.query(models.Usuario).offset(skip).limit(limit).all()


def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    """Crea un usuario nuevo junto con su ecosistema inicial (Pasaporte, Árbol, Libro)."""
    email_limpio = usuario.email.strip().lower()

    # Verificar si el correo ya existe
    usuario_existente = obtener_usuario_por_email(db, email=email_limpio)
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado.",
        )

    try:
        # Hashear contraseña de forma segura con el método nativo
        hashed_pwd = security.get_password_hash(usuario.password)

        # Crear Usuario base
        db_usuario = models.Usuario(
            nombre=usuario.nombre.strip(),
            email=email_limpio,
            hashed_password=hashed_pwd,
            rol=usuario.rol or "estudiante",
            activo=True,
        )
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)

        # Crear relaciones iniciales del ecosistema gamificado
        db_pasaporte = models.Pasaporte(
            usuario_id=db_usuario.id, nivel_actual=1, puntos_experiencia=0
        )
        db.add(db_pasaporte)

        db_arbol = models.ArbolProgreso(
            usuario_id=db_usuario.id,
            estado_crecimiento="semilla",
            energia_vital=100,
        )
        db.add(db_arbol)

        db_libro = models.LibroVivo(
            usuario_id=db_usuario.id, capitulo_actual=1, paginas_completadas=0
        )
        db.add(db_libro)

        db.commit()
        db.refresh(db_usuario)

        return db_usuario

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en la base de datos: {str(e.orig)}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo interno al inicializar entidades: {str(e)}",
        )


def crear_mision_usuario(db: Session, mision: schemas.MisionCrear, usuario_id: int):
    """Crea una misión asignada a un usuario específico."""
    db_mision = models.MisionUsuario(
        usuario_id=usuario_id,
        titulo_mision=mision.titulo_mision,
        recompensa_puntos=mision.recompensa_puntos,
        estado="pendiente",
    )
    db.add(db_mision)
    db.commit()
    db.refresh(db_mision)
    return db_mision


def obtener_misiones_usuario(db: Session, usuario_id: int):
    """Obtiene todas las misiones asociadas a un usuario."""
    return (
        db.query(models.MisionUsuario)
        .filter(models.MisionUsuario.usuario_id == usuario_id)
        .all()
    )


def completar_mision(db: Session, usuario_id: int, mision_id: int):
    """Marca una misión como completada y otorga experiencia al pasaporte del usuario."""
    mision = (
        db.query(models.MisionUsuario)
        .filter(
            models.MisionUsuario.id == mision_id,
            models.MisionUsuario.usuario_id == usuario_id,
            models.MisionUsuario.estado == "pendiente",
        )
        .first()
    )

    if not mision:
        return None

    mision.estado = "completada"

    # Sumar puntos al pasaporte
    pasaporte = (
        db.query(models.Pasaporte)
        .filter(models.Pasaporte.usuario_id == usuario_id)
        .first()
    )
    if pasaporte:
        pasaporte.puntos_experiencia += mision.recompensa_puntos

    db.commit()
    db.refresh(mision)
    return mision


def obtener_libro_vivo(db: Session, usuario_id: int):
    """Obtiene el registro del Libro Vivo de un usuario."""
    return (
        db.query(models.LibroVivo)
        .filter(models.LibroVivo.usuario_id == usuario_id)
        .first()
    )


def registrar_interaccion(
    db: Session, usuario_id: int, interaccion: schemas.InteraccionCrear
):
    """Registra una interacción de chat con XiXi en la base de datos."""
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
