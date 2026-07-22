from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import engine, get_db
import ia_service  # <-- NUEVA IMPORTACIÓN

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


@app.post(
    "/usuarios/",
    response_model=schemas.UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
)
def crear_nuevo_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
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
        # Sobrescribir el campo vacío con la respuesta generada
        interaccion.respuesta_guia = respuesta_ia
    elif not interaccion.respuesta_guia:
        # Fallback en caso de que sea otro personaje aún no programado
        interaccion.respuesta_guia = (
            "Aún estoy aprendiendo a comunicarme. ¡Pronto podré hablar contigo!"
        )

    # 3. Guardar la transacción completa en la base de datos
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
