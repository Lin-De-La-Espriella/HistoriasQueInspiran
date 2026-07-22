from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import engine, get_db

# Crear tablas en la base de datos de forma automática
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Historias que Inspiran API",
    description="Motor principal de la plataforma EdTech",
    version="0.1.0",
)


@app.get("/", tags=["General"])
def ruta_principal():
    return {
        "estado": "En línea",
        "mensaje": "El cerebro de Historias que Inspiran está funcionando y conectado a PostgreSQL.",
    }


# Endpoint 1: Crear Usuario
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


# Endpoint 2: Listar Usuarios
@app.get("/usuarios/", response_model=List[schemas.UsuarioRespuesta], tags=["Usuarios"])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_usuarios(db=db, skip=skip, limit=limit)
