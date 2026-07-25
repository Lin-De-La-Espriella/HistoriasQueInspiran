from datetime import timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Imports directos (compatibles con Root Directory = backend en Render y ejecución local)
from backend import models, schemas, crud, security, ia_service
from backend.database import engine, get_db

# Inicialización de la base de datos
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
# SECCIÓN: AUTENTICACIÓN (LOGIN SEPARADO Y LIMPIO)
# ==========================================


class LoginSchema(BaseModel):
    email: str
    password: str


@app.post("/auth/login", response_model=schemas.Token, tags=["Autenticación"])
def login_plataforma_json(login_data: LoginSchema, db: Session = Depends(get_db)):
    """
    Endpoint exclusivo para Streamlit: Recibe JSON puro y evita conflictos de formularios.
    """
    email = login_data.email.strip().lower()
    password = login_data.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Por favor ingresa un correo y una contraseña válidos.",
        )

    usuario = crud.autenticar_usuario(db, email=email, password_plana=password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.crear_token_acceso(
        data={"sub": usuario.email, "usuario_id": usuario.id, "rol": usuario.rol},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.post("/token", response_model=schemas.Token, tags=["Autenticación"])
def login_para_obtener_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Endpoint exclusivo para Swagger UI / OAuth2: Recibe Form-Data.
    """
    usuario = crud.obtener_usuario_por_email(db, email=form_data.username.strip())
    if not usuario or not security.verificar_password(
        form_data.password.strip(), usuario.hashed_password.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.crear_token_acceso(
        data={"sub": usuario.email, "usuario_id": usuario.id, "rol": usuario.rol}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==========================================
# SECCIÓN: REGLAS DE NEGOCIO (CORE GAMIFICADO)
# ==========================================


def calcular_nivel_por_xp(xp_totales: int) -> int:
    """
    Calcula el nivel dinámico usando la curva progresiva:
    XP acumulados necesarios para Nivel N = 50 * N * (N - 1)
    """
    nivel = 1
    xp_necesaria = 0
    while True:
        xp_siguiente = nivel * 100
        if xp_totales < xp_necesaria + xp_siguiente:
            break
        xp_necesaria += xp_siguiente
        nivel += 1
    return nivel


def evaluar_y_actualizar_arbol(db, arbol_obj, pasaporte_obj):
    """
    Modelado Lógico para la evolución de 10 Fases Biológicas en función del Nivel.
    """
    pasaporte_obj.nivel_actual = calcular_nivel_por_xp(pasaporte_obj.puntos_experiencia)
    nivel = pasaporte_obj.nivel_actual

    fases = {
        1: ("semilla", 100),
        2: ("brote_menor", 120),
        3: ("brote_explorador", 130),
        4: ("arbol_joven_enraizado", 140),
        5: ("arbol_joven_creativo", 150),
        6: ("arbol_joven_empatico", 175),
        7: ("arbol_frondoso_lider", 200),
        8: ("arbol_frondoso_visionario", 225),
        9: ("arbol_frondoso_sabio", 250),
        10: ("arbol_cosmico", 300),
    }

    estado, energia = fases.get(nivel, ("arbol_cosmico", 300))
    arbol_obj.estado_crecimiento = estado

    if arbol_obj.energia_vital < energia:
        arbol_obj.energia_vital = energia

    db.commit()
    db.refresh(arbol_obj)
    db.refresh(pasaporte_obj)


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
    try:
        return crud.crear_usuario(db=db, usuario=usuario)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo crítico en la arquitectura de datos: {str(e)}",
        )


@app.get("/usuarios/", response_model=List[schemas.UsuarioRespuesta], tags=["Usuarios"])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_usuarios(db=db, skip=skip, limit=limit)


@app.put("/usuarios/{usuario_id}/misiones/{mision_id}/completar")
def completar_mision(usuario_id: int, mision_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para marcar una misión como completada.
    Se ha ajustado la seguridad temporalmente para permitir el flujo en Modo Dev.
    """
    mision = (
        db.query(models.Mision)
        .filter(models.Mision.id == mision_id, models.Mision.usuario_id == usuario_id)
        .first()
    )

    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    if mision.estado == "completada":
        return {"mensaje": "La misión ya estaba completada", "mision": mision}

    # Actualizamos el estado a completada
    mision.estado = "completada"
    db.commit()
    db.refresh(mision)

    return {"mensaje": "Misión completada con éxito", "mision": mision}


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
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
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
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
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
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    mision_actualizada = crud.completar_mision(
        db=db, usuario_id=usuario_id, mision_id=mision_id
    )

    if not mision_actualizada:
        raise HTTPException(
            status_code=400,
            detail="Operación rechazada: La misión no existe o ya fue reclamada.",
        )

    db_usuario = (
        db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    )
    if db_usuario and db_usuario.arbol and db_usuario.pasaporte:
        evaluar_y_actualizar_arbol(db, db_usuario.arbol, db_usuario.pasaporte)

    return mision_actualizada


# ==========================================
# SECCIÓN: creación automática de la misión
# ==========================================


@app.post("/usuarios/{usuario_id}/misiones/generar_ia")
def crear_mision_personalizada_ia(usuario_id: int, db: Session = Depends(get_db)):
    """
    Endpoint que invoca a XiXi vía Groq Cloud para crear una misión dinámica guardada en Supabase.
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    estado_arbol = user.arbol.estado_crecimiento if user.arbol else "semilla"
    nivel = user.pasaporte.nivel_actual if user.pasaporte else 1

    # Invocación a Groq (Llama 3.3 70B)
    datos_mision = ia_service.generar_mision_ia(
        estado_arbol=estado_arbol, nivel_usuario=nivel
    )

    # Creación del modelo con TODOS los campos obligatorios mapeados
    nueva_mision = models.Mision(
        usuario_id=usuario_id,
        titulo_mision=datos_mision.get("titulo_mision", "Desafío de Evolución"),
        descripcion=datos_mision.get(
            "descripcion",
            "Completa este hito estratégico para impulsar tu crecimiento.",
        ),
        recompensa_puntos=datos_mision.get("recompensa_puntos", 50),
        estado="pendiente",
    )

    db.add(nueva_mision)
    db.commit()
    db.refresh(nueva_mision)

    return nueva_mision


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
    libro = crud.obtener_libro_vivo(db=db, usuario_id=usuario_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro Vivo no encontrado.")

    libro.paginas_completadas += 1

    if libro.paginas_completadas >= 5:
        libro.capitulo_actual += 1
        libro.paginas_completadas = 0

    db.commit()
    db.refresh(libro)
    return libro


# ==========================================
# SECCIÓN: GUÍAS IA (CHAT E INTERACCIONES)
# ==========================================


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

    analisis_ia = ia_service.generar_analisis_xixi(
        mensaje_usuario=mensaje, estado_arbol=estado_arbol, nivel_usuario=nivel_usuario
    )

    xp_ganado = analisis_ia.get("xp_ganado", 5)
    energia_ganada = analisis_ia.get("energia_ganada", 2)
    respuesta_xixi = analisis_ia.get("respuesta_guia", "Frecuencia recibida.")

    interaccion.respuesta_guia = respuesta_xixi

    nueva_interaccion = crud.registrar_interaccion(
        db=db, usuario_id=usuario_id, interaccion=interaccion
    )

    if db_usuario.pasaporte:
        db_usuario.pasaporte.puntos_experiencia += xp_ganado
        nuevo_nivel = (db_usuario.pasaporte.puntos_experiencia // 100) + 1
        db_usuario.pasaporte.nivel_actual = nuevo_nivel

    if db_usuario.arbol:
        db_usuario.arbol.energia_vital += energia_ganada
        evaluar_y_actualizar_arbol(db, db_usuario.arbol, db_usuario.pasaporte)

    db.commit()

    return {
        "id": nueva_interaccion.id,
        "respuesta_guia": respuesta_xixi,
        "emocion_detectada": analisis_ia.get("emocion_detectada", "N/A"),
        "xp_ganado": xp_ganado,
        "energia_ganada": energia_ganada,
    }


@app.post("/usuarios/{usuario_id}/evolucionar")
def evaluar_evolucion_usuario(
    usuario_id: int, xp_ganado: int, db: Session = Depends(get_db)
):
    """
    Evalúa de forma lógica el progreso del usuario, actualiza su XP,
    calcula su nuevo nivel y ajusta la fase de su bio-estructura.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Acumular XP (asumiendo que el modelo tiene campos xp_totales y nivel)
    usuario.xp_totales = (usuario.xp_totales or 0) + xp_ganado

    # Regla de negocio para escalado de niveles (Ej: 100 XP por nivel)
    nuevo_nivel = (usuario.xp_totales // 100) + 1

    if nuevo_nivel > (usuario.nivel or 1):
        usuario.nivel = nuevo_nivel
        # Aquí podemos disparar la evolución de la bio-estructura asociada

    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Evolución procesada con éxito bajo mejora continua.",
        "xp_totales": usuario.xp_totales,
        "nivel_actual": usuario.nivel,
    }
