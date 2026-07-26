from datetime import timedelta
from typing import List
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
# SECCIÓN: AUTENTICACIÓN (LOGIN SEPARADO Y LIMPIO)
# ==========================================


class LoginSchema(BaseModel):
    email: str
    password: str


@app.post("/auth/login", response_model=schemas.Token, tags=["Autenticación"])
def login_plataforma_json(login_data: LoginSchema, db: Session = Depends(get_db)):
    """Endpoint exclusivo para Streamlit: Recibe JSON puro y evita conflictos de formularios."""
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

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token", response_model=schemas.Token, tags=["Autenticación"])
def login_para_obtener_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Endpoint exclusivo para Swagger UI / OAuth2: Recibe Form-Data."""
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
    """Calcula el nivel dinámico: (XP Totales // 100) + 1"""
    return (xp_totales // 100) + 1


def evaluar_y_actualizar_arbol(db, arbol_obj, pasaporte_obj):
    """
    Modelado Lógico para la evolución de Fases Biológicas y Gestión de Insignias.
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

    # --- LÓGICA DE INSIGNIAS DINÁMICAS ---
    insignias_actuales = pasaporte_obj.insignias or []
    if not isinstance(insignias_actuales, list):
        insignias_actuales = []

    nuevas_insignias = list(insignias_actuales)

    if nivel >= 1 and "🛸 Primer Contacto" not in nuevas_insignias:
        nuevas_insignias.append("🛸 Primer Contacto")

    if nivel >= 3 and "🏅 Brote Explorador" not in nuevas_insignias:
        nuevas_insignias.append("🏅 Brote Explorador")

    if nivel >= 5 and "🌳 Líder Enraizado" not in nuevas_insignias:
        nuevas_insignias.append("🌳 Líder Enraizado")

    pasaporte_obj.insignias = nuevas_insignias

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
# SECCIÓN: GAMIFICACIÓN (MISIONES - MODO DEV ACTIVO)
# ==========================================


@app.post("/usuarios/{usuario_id}/misiones/generar_ia", tags=["Gamificación"])
def crear_mision_personalizada_ia(usuario_id: int, db: Session = Depends(get_db)):
    """Endpoint que invoca a XiXi vía Groq Cloud para crear una misión dinámica."""
    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    estado_arbol = user.arbol.estado_crecimiento if user.arbol else "semilla"
    nivel = user.pasaporte.nivel_actual if user.pasaporte else 1

    datos_mision = ia_service.generar_mision_ia(
        estado_arbol=estado_arbol, nivel_usuario=nivel
    )

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


@app.get("/usuarios/{usuario_id}/misiones/", tags=["Gamificación"])
def obtener_misiones_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),  # 🔒 Blindado
):
    misiones = (
        db.query(models.Mision).filter(models.Mision.usuario_id == usuario_id).all()
    )
    return misiones


@app.put("/usuarios/{usuario_id}/misiones/{mision_id}/completar", tags=["Gamificación"])
def completar_mision(
    usuario_id: int,
    mision_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),  # 🔒 Blindado
):
    # ... lógica de completado y avance de libro vivo ...
    """Endpoint para marcar una misión como completada y escribir en el Libro Vivo"""
    mision = (
        db.query(models.Mision)
        .filter(models.Mision.id == mision_id, models.Mision.usuario_id == usuario_id)
        .first()
    )

    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    if mision.estado == "completada":
        return {"mensaje": "La misión ya estaba completada", "mision": mision}

    # 1. Marcar misión como completada
    mision.estado = "completada"

    # 2. Asignar XP y actualizar árbol
    db_usuario = (
        db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    )
    if db_usuario and db_usuario.pasaporte:
        db_usuario.pasaporte.puntos_experiencia += mision.recompensa_puntos
        if db_usuario.arbol:
            evaluar_y_actualizar_arbol(db, db_usuario.arbol, db_usuario.pasaporte)

        # 3. AVANCE AUTOMÁTICO DEL LIBRO VIVO
        if db_usuario.libro_vivo:
            db_usuario.libro_vivo.paginas_completadas += 1
            if db_usuario.libro_vivo.paginas_completadas >= 5:
                db_usuario.libro_vivo.capitulo_actual += 1
                db_usuario.libro_vivo.paginas_completadas = 0

    db.commit()
    db.refresh(mision)
    return {
        "mensaje": "Misión completada y página del Libro Vivo registrada",
        "mision": mision,
    }


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
    # NOTA: Este aún requiere Token, evalúa si lo usarás en Dev Mode
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
    # NOTA: Remueve la dependencia si presentas 401 Unauthorized en el chat
    # usuario_actual: dict = Depends(security.obtener_usuario_actual),
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


@app.post("/usuarios/{usuario_id}/evolucionar", tags=["Gamificación"])
def evaluar_evolucion_usuario(
    usuario_id: int, xp_ganado: int, db: Session = Depends(get_db)
):
    """Endpoint corregido para acceder correctamente a las relaciones del modelo"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

    if not usuario or not usuario.pasaporte:
        raise HTTPException(status_code=404, detail="Usuario o Pasaporte no encontrado")

    usuario.pasaporte.puntos_experiencia += xp_ganado

    if usuario.arbol:
        evaluar_y_actualizar_arbol(db, usuario.arbol, usuario.pasaporte)
    else:
        usuario.pasaporte.nivel_actual = calcular_nivel_por_xp(
            usuario.pasaporte.puntos_experiencia
        )

    db.commit()
    db.refresh(usuario.pasaporte)

    return {
        "mensaje": "Evolución procesada con éxito bajo mejora continua.",
        "xp_totales": usuario.pasaporte.puntos_experiencia,
        "nivel_actual": usuario.pasaporte.nivel_actual,
    }


@app.post("/usuarios/{usuario_id}/reset-base-cero", tags=["Dev Mode"])
def resetear_usuario_base_cero(usuario_id: int, db: Session = Depends(get_db)):
    """Endpoint de desarrollo para reiniciar un usuario a Nivel 1 y 0 XP"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Reset Pasaporte
    if usuario.pasaporte:
        usuario.pasaporte.puntos_experiencia = 0
        usuario.pasaporte.nivel_actual = 1

    # Reset Árbol
    if usuario.arbol:
        usuario.arbol.estado_crecimiento = "semilla"
        usuario.arbol.energia_vital = 100

    # Reset Libro
    if usuario.libro_vivo:
        usuario.libro_vivo.capitulo_actual = 1
        usuario.libro_vivo.paginas_completadas = 0

    # Limpiar Misiones antiguas
    db.query(models.Mision).filter(models.Mision.usuario_id == usuario_id).delete()

    db.commit()
    return {"mensaje": "Usuario reiniciado a Base Cero con éxito."}
