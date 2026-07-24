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
from pydantic import BaseModel
import random

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
# SECCIÓN: REGLAS DE NEGOCIO (CORE LÓGICO)
# ==========================================


def evaluar_y_actualizar_arbol(db, arbol_obj, pasaporte_obj):
    """
    Modelado Lógico para la evolución de 10 Fases Biológicas (0 a 1000 XP).
    """
    xp = pasaporte_obj.puntos_experiencia

    # Mapeo lineal según los 10 Capítulos
    if xp >= 1000:
        arbol_obj.estado_crecimiento = "arbol_cosmico"
        arbol_obj.energia_vital = 300
    elif xp >= 800:
        arbol_obj.estado_crecimiento = "arbol_frondoso_sabio"
        arbol_obj.energia_vital = 250
    elif xp >= 700:
        arbol_obj.estado_crecimiento = "arbol_frondoso_visionario"
        arbol_obj.energia_vital = 225
    elif xp >= 600:
        arbol_obj.estado_crecimiento = "arbol_frondoso_lider"
        arbol_obj.energia_vital = 200
    elif xp >= 500:
        arbol_obj.estado_crecimiento = "arbol_joven_empatico"
        arbol_obj.energia_vital = 175
    elif xp >= 400:
        arbol_obj.estado_crecimiento = "arbol_joven_creativo"
        arbol_obj.energia_vital = 150
    elif xp >= 300:
        arbol_obj.estado_crecimiento = "arbol_joven_enraizado"
        arbol_obj.energia_vital = 140
    elif xp >= 200:
        arbol_obj.estado_crecimiento = "brote_explorador"
        arbol_obj.energia_vital = 130
    elif xp >= 100:
        arbol_obj.estado_crecimiento = "brote_menor"
        arbol_obj.energia_vital = 120
    else:
        arbol_obj.estado_crecimiento = "semilla"
        arbol_obj.energia_vital = 100

    db.commit()
    db.refresh(arbol_obj)


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
    usuario_id: int,
    mision: schemas.MisionCrear,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(
        security.obtener_usuario_actual
    ),  # 🔒 RUTA PROTEGIDA
):
    return crud.crear_mision_usuario(db=db, mision=mision, usuario_id=usuario_id)


@app.get(
    "/usuarios/{usuario_id}/misiones/",
    response_model=List[schemas.MisionRespuesta],
    tags=["Gamificación"],
)
def ver_misiones(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(
        security.obtener_usuario_actual
    ),  # 🔒 RUTA PROTEGIDA
):
    return crud.obtener_misiones_usuario(db=db, usuario_id=usuario_id)


@app.put(
    "/usuarios/{usuario_id}/misiones/{mision_id}/completar",
    response_model=schemas.MisionRespuesta,
    tags=["Gamificación"],
)
def completar_mision_usuario(
    usuario_id: int,
    mision_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(
        security.obtener_usuario_actual
    ),  # 🔒 RUTA PROTEGIDA
):
    # 1. Completar misión en la BD (suma experiencia)
    mision_actualizada = crud.completar_mision(
        db=db, usuario_id=usuario_id, mision_id=mision_id
    )

    if not mision_actualizada:
        raise HTTPException(
            status_code=400,
            detail="Operación rechazada: La misión no existe o ya fue reclamada.",
        )

    # 2. Extraer usuario para evaluar evolución del árbol
    db_usuario = (
        db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    )
    if db_usuario and db_usuario.arbol and db_usuario.pasaporte:
        evaluar_y_actualizar_arbol(db, db_usuario.arbol, db_usuario.pasaporte)

    return mision_actualizada


# ==========================================
# SECCIÓN: LIBRO VIVO (AVANCE)
# ==========================================


@app.put(
    "/usuarios/{usuario_id}/libro/avanzar-pagina",
    response_model=schemas.LibroVivoRespuesta,
    tags=["Libro Vivo"],
)
def escribir_pagina_libro(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    """
    Suma una página al Libro Vivo. Al llegar a 5 páginas,
    avanza automáticamente de capítulo y reinicia el contador de hojas.
    """
    libro = crud.obtener_libro_vivo(db=db, usuario_id=usuario_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro Vivo no encontrado.")

    libro.paginas_completadas += 1

    # Lógica de cierre de capítulo
    if libro.paginas_completadas >= 5:
        libro.capitulo_actual += 1
        libro.paginas_completadas = 0

    db.commit()
    db.refresh(libro)
    return libro


@app.post(
    "/usuarios/{usuario_id}/interacciones/",
    status_code=status.HTTP_201_CREATED,
    tags=["Guías IA"],
)
def guardar_interaccion(
    usuario_id: int,
    interaccion: schemas.InteraccionCrear,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    """
    Motor Psico-Pedagógico de XiXi 2.0:
    Utiliza Prompt Engineering avanzado para asignar recompensas dinámicas.
    """
    # 1. Obtener el contexto del usuario
    db_usuario = (
        db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    )
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    mensaje = interaccion.mensaje_usuario.strip()
    estado_arbol = (
        db_usuario.arbol.estado_crecimiento if db_usuario.arbol else "semilla"
    )
    nivel_usuario = db_usuario.pasaporte.nivel_actual if db_usuario.pasaporte else 1

    # 2. Inferencia de IA: Evaluación del mensaje
    analisis_ia = ia_service.generar_analisis_xixi(
        mensaje_usuario=mensaje, estado_arbol=estado_arbol, nivel_usuario=nivel_usuario
    )

    xp_ganado = analisis_ia.get("xp_ganado", 5)
    energia_ganada = analisis_ia.get("energia_ganada", 2)
    respuesta_xixi = analisis_ia.get("respuesta_guia", "Frecuencia recibida.")

    interaccion.respuesta_guia = respuesta_xixi

    # 3. Registrar la interacción en BD
    nueva_interaccion = crud.registrar_interaccion(
        db=db, usuario_id=usuario_id, interaccion=interaccion
    )

    # 4. Actualizar Pasaporte (XP y Nivel)
    if db_usuario.pasaporte:
        db_usuario.pasaporte.puntos_experiencia += xp_ganado
        nuevo_nivel = (db_usuario.pasaporte.puntos_experiencia // 100) + 1
        db_usuario.pasaporte.nivel_actual = nuevo_nivel

    # 5. Actualizar Árbol (Energía Vital) y evaluar evolución
    if db_usuario.arbol:
        db_usuario.arbol.energia_vital += energia_ganada
        evaluar_y_actualizar_arbol(db, db_usuario.arbol, db_usuario.pasaporte)

    # 6. 🤖 LÓGICA DE AUTO-ESCRITURA EN EL LIBRO VIVO
    total_interacciones = (
        db.query(models.InteraccionGuia)
        .filter(models.InteraccionGuia.usuario_id == usuario_id)
        .count()
    )

    if total_interacciones > 0 and total_interacciones % 3 == 0:
        libro = crud.obtener_libro_vivo(db=db, usuario_id=usuario_id)
        if libro:
            libro.paginas_completadas += 1
            if libro.paginas_completadas >= 5:
                libro.capitulo_actual += 1
                libro.paginas_completadas = 0
            db.add(libro)

    db.commit()

    return {
        "id": nueva_interaccion.id,
        "respuesta_guia": respuesta_xixi,
        "emocion_detectada": analisis_ia.get("emocion_detectada", "N/A"),
        "xp_ganado": xp_ganado,
        "energia_ganada": energia_ganada,
    }
