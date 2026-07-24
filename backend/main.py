from datetime import timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
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
# SECCIÓN: AUTENTICACIÓN HÍBRIDA (JSON & FORM)
# ==========================================


class LoginSchema(BaseModel):
    email: str
    password: str


@app.post("/auth/login", response_model=schemas.Token, tags=["Autenticación"])
@app.post("/token", response_model=schemas.Token, tags=["Autenticación"])
def login_usuario_universal(
    login_data: Optional[LoginSchema] = None,
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(None),
    db: Session = Depends(get_db),
):
    """
    Endpoint híbrido y robusto: Soporta peticiones JSON (Streamlit)
    y Form-Data (Swagger / OAuth2) evitando errores 422 y 500.
    """
    email = None
    password = None

    # 1. Extracción desde formato JSON
    if login_data and login_data.email and login_data.password:
        email = login_data.email.strip().lower()
        password = login_data.password.strip()

    # 2. Extracción desde formato Form-Data (OAuth2)
    elif form_data and form_data.username and form_data.password:
        email = form_data.username.strip().lower()
        password = form_data.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Por favor ingresa un correo y una contraseña válidos.",
        )

    # 3. Autenticación centralizada mediante CRUD
    usuario = crud.autenticar_usuario(db, email=email, password_plana=password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"Www-Authenticate": "Bearer"},
        )

    # 4. Emisión de Token JWT seguro
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.crear_token_acceso(
        data={"sub": usuario.email, "usuario_id": usuario.id, "rol": usuario.rol},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


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
