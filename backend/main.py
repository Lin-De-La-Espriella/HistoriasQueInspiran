from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
import security
import ia_service
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Historias que Inspiran API",
    description="Motor principal de la plataforma EdTech y Gamificación",
    version="0.2.0",
)


@app.get("/", tags=["General"])
def ruta_principal():
    return {
        "estado": "En línea",
        "mensaje": "El cerebro de Historias que Inspiran está funcionando con el motor de Gamificación.",
    }


# ==========================================
# SECCIÓN: USUARIOS (REGISTRO Y LISTADO)
# ==========================================


@app.post(
    "/usuarios/",
    response_model=schemas.UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
)
def crear_nuevo_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    """
    Endpoint para registrar un nuevo usuario y crear su ecosistema inicial.
    """
    db_usuario = crud.obtener_usuario_por_email(db, email=usuario.email)
    if db_usuario:
        raise HTTPException(
            status_code=400,
            detail="Este correo electrónico ya está registrado en la plataforma.",
        )
    return crud.crear_usuario(db=db, usuario=usuario)


@app.get("/usuarios/", response_model=List[schemas.UsuarioRespuesta], tags=["Usuarios"])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_usuarios(db=db, skip=skip, limit=limit)


# ==========================================
# SECCIÓN: AUTENTICACIÓN (LOGIN)
# ==========================================


@app.post("/token", response_model=schemas.Token, tags=["Autenticación"])
def login_para_obtener_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Endpoint para autenticar usuarios mediante OAuth2 (Email y Password)
    y generar un Token de acceso JWT.
    """
    # 1. Buscar al usuario por correo
    usuario = crud.obtener_usuario_por_email(db, email=form_data.username)

    # 2. Validar existencia del usuario
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Validar contraseña
    if not security.verificar_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Generar el Token de acceso JWT firmado
    access_token = security.crear_token_acceso(
        data={"sub": usuario.email, "usuario_id": usuario.id, "rol": usuario.rol}
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ==========================================
# SECCIÓN: GAMIFICACIÓN (MISIONES)
# ==========================================


@app.post(
    "/usuarios/{usuario_id}/misiones/",
    response_model=schemas.MisionRespuesta,
    status_code=status.HTTP_201_CREATED,
    tags=["Gamificación"],
)
def asignarle_mision(
    usuario_id: int, mision: schemas.MisionCrear, db: Session = Depends(get_db)
):
    return crud.crear_mision_usuario(db=db, mision=mision, usuario_id=usuario_id)


@app.get(
    "/usuarios/{usuario_id}/misiones/",
    response_model=List[schemas.MisionRespuesta],
    tags=["Gamificación"],
)
def ver_misiones(usuario_id: int, db: Session = Depends(get_db)):
    return crud.obtener_misiones_usuario(db=db, usuario_id=usuario_id)


@app.put(
    "/usuarios/{usuario_id}/misiones/{mision_id}/completar",
    response_model=schemas.MisionRespuesta,
    tags=["Gamificación"],
)
def completar_mision_usuario(
    usuario_id: int, mision_id: int, db: Session = Depends(get_db)
):
    mision_actualizada = crud.completar_mision(
        db=db, usuario_id=usuario_id, mision_id=mision_id
    )

    if not mision_actualizada:
        raise HTTPException(
            status_code=400,
            detail="Operación rechazada: La misión no existe o ya fue reclamada.",
        )
    return mision_actualizada


# ==========================================
# SECCIÓN: LIBRO VIVO
# ==========================================


@app.get(
    "/usuarios/{usuario_id}/libro/",
    response_model=schemas.LibroVivoRespuesta,
    tags=["Libro Vivo"],
)
def ver_libro_vivo(usuario_id: int, db: Session = Depends(get_db)):
    libro = crud.obtener_libro_vivo(db=db, usuario_id=usuario_id)
    if not libro:
        raise HTTPException(
            status_code=404, detail="Libro vivo no encontrado para este usuario."
        )
    return libro


# ==========================================
# SECCIÓN: GUÍAS IA (CHAT)
# ==========================================


@app.post(
    "/usuarios/{usuario_id}/interacciones/",
    response_model=schemas.InteraccionRespuesta,
    status_code=status.HTTP_201_CREATED,
    tags=["Guías IA"],
)
def guardar_interaccion(
    usuario_id: int,
    interaccion: schemas.InteraccionCrear,
    db: Session = Depends(get_db),
):

    # 1. Obtener el contexto del usuario desde la base de datos
    db_usuario = (
        db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    )
    if not db_usuario:
        raise HTTPException(
            status_code=404, detail="Usuario no encontrado en la plataforma."
        )

    # Extraer variables para el Prompt
    estado_arbol = (
        db_usuario.arbol.estado_crecimiento if db_usuario.arbol else "semilla"
    )
    nivel_usuario = db_usuario.pasaporte.nivel_actual if db_usuario.pasaporte else 1

    # 2. Inyectar la Inteligencia Artificial si el personaje es XiXi
    if interaccion.personaje.lower() == "xixi":
        respuesta_ia = ia_service.generar_respuesta_xixi(
            mensaje_usuario=interaccion.mensaje_usuario,
            estado_arbol=estado_arbol,
            nivel_usuario=nivel_usuario,
        )
        interaccion.respuesta_guia = respuesta_ia
    elif not interaccion.respuesta_guia:
        interaccion.respuesta_guia = (
            "Aún estoy aprendiendo a comunicarme. ¡Pronto podré hablar contigo!"
        )

    # 3. Guardar la transacción completa
    return crud.registrar_interaccion(
        db=db, usuario_id=usuario_id, interaccion=interaccion
    )


@app.get(
    "/usuarios/{usuario_id}/interacciones/",
    response_model=List[schemas.InteraccionRespuesta],
    tags=["Guías IA"],
)
def ver_historial_chat(usuario_id: int, db: Session = Depends(get_db)):
    return crud.obtener_historial_interacciones(db=db, usuario_id=usuario_id)
