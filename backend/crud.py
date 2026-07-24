from backend import models, schemas, security
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    # 1. Verificar si el correo ya existe antes de intentar insertar
    usuario_existente = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == usuario.email.strip())
        .first()
    )
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado.",
        )

    try:
        # 2. Hashear contraseña
        hashed_pwd = security.get_password_hash(usuario.password.strip())

        # 3. Crear Usuario base
        db_usuario = models.Usuario(
            nombre=usuario.nombre.strip(),
            email=usuario.email.strip(),
            hashed_password=hashed_pwd,
            rol="estudiante",
            activo=True,
        )
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)

        # 4. Crear relaciones iniciales
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

        # Confirmar todas las relaciones
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
