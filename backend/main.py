from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend import crud, ia_service, models, schemas, security
from backend.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Historias que Inspiran API",
    description="Motor principal de la plataforma EdTech y Gamificación",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BIO_MAP = {
    1: {"estado": "semilla", "label": "🌱 Semilla", "energia": 100},
    2: {"estado": "brote_menor", "label": "🌿 Brote Menor", "energia": 120},
    3: {"estado": "brote_explorador", "label": "🌿 Brote Explorador", "energia": 130},
    4: {
        "estado": "arbol_joven_enraizado",
        "label": "🌳 Árbol Joven Enraizado",
        "energia": 140,
    },
    5: {
        "estado": "arbol_joven_creativo",
        "label": "🌳 Árbol Joven Creativo",
        "energia": 150,
    },
    6: {
        "estado": "arbol_joven_empatico",
        "label": "🌳 Árbol Joven Empático",
        "energia": 175,
    },
    7: {
        "estado": "arbol_frondoso_lider",
        "label": "🌲 Árbol Frondoso Líder",
        "energia": 200,
    },
    8: {
        "estado": "arbol_frondoso_visionario",
        "label": "🌲 Árbol Frondoso Visionario",
        "energia": 225,
    },
    9: {
        "estado": "arbol_frondoso_sabio",
        "label": "🌲 Árbol Frondoso Sabio",
        "energia": 250,
    },
    10: {"estado": "arbol_cosmico", "label": "✨ Árbol Cósmico", "energia": 300},
}


class LoginSchema(BaseModel):
    email: str
    password: str


def _verificar_propietario(usuario_actual: dict, usuario_id: int):
    usuario_actual_id = usuario_actual.get("usuario_id")
    if usuario_actual_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o incompleto.",
        )
    if int(usuario_actual_id) != int(usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este usuario.",
        )


@app.get("/", tags=["General"])
def ruta_principal():
    return {
        "estado": "En línea",
        "mensaje": "El cerebro de Historias que Inspira está funcionando.",
    }


@app.post("/auth/login", response_model=schemas.LoginRespuesta, tags=["Autenticación"])
def login_plataforma_json(login_data: LoginSchema, db: Session = Depends(get_db)):
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
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "rol": usuario.rol,
    }


@app.post("/token", response_model=schemas.LoginRespuesta, tags=["Autenticación"])
def login_para_obtener_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = crud.obtener_usuario_por_email(
        db, email=form_data.username.strip().lower()
    )
    if not usuario or not security.verificar_password(
        form_data.password.strip(), usuario.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.crear_token_acceso(
        data={"sub": usuario.email, "usuario_id": usuario.id, "rol": usuario.rol}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "rol": usuario.rol,
    }


def calcular_nivel_por_xp(xp_totales: int) -> int:
    return (xp_totales // 100) + 1


def evaluar_y_actualizar_arbol(db: Session, arbol_obj, pasaporte_obj):
    pasaporte_obj.nivel_actual = calcular_nivel_por_xp(pasaporte_obj.puntos_experiencia)
    nivel = pasaporte_obj.nivel_actual
    info = BIO_MAP.get(nivel, BIO_MAP[10])

    arbol_obj.estado_crecimiento = info["estado"]
    if arbol_obj.energia_vital < info["energia"]:
        arbol_obj.energia_vital = info["energia"]

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

    if nivel >= 7 and "🌲 Guía del Bosque" not in nuevas_insignias:
        nuevas_insignias.append("🌲 Guía del Bosque")

    if nivel >= 10 and "✨ Creador Cósmico" not in nuevas_insignias:
        nuevas_insignias.append("✨ Creador Cósmico")

    pasaporte_obj.insignias = nuevas_insignias
    db.commit()
    db.refresh(arbol_obj)
    db.refresh(pasaporte_obj)


@app.post(
    "/usuarios/",
    response_model=schemas.UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
)
def crear_nuevo_usuario(
    usuario: schemas.UsuarioCrear,
    db: Session = Depends(get_db),
):
    return crud.crear_usuario(db=db, usuario=usuario)


@app.get(
    "/usuarios/",
    response_model=List[schemas.UsuarioRespuesta],
    tags=["Usuarios"],
)
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.obtener_usuarios(db=db, skip=skip, limit=limit)


@app.post("/usuarios/{usuario_id}/misiones/generar_ia", tags=["Gamificación"])
def crear_mision_personalizada_ia(
    usuario_id: int,
    enfoque: str = "emprendimiento",
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    _verificar_propietario(usuario_actual, usuario_id)

    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    estado_arbol = user.arbol.estado_crecimiento if user.arbol else "semilla"
    nivel = user.pasaporte.nivel_actual if user.pasaporte else 1

    datos_mision = ia_service.generar_mision_ia(
        estado_arbol=estado_arbol,
        nivel_usuario=nivel,
        enfoque=enfoque,
    )

    nueva_mision = models.Mision(
        usuario_id=usuario_id,
        titulo_mision=datos_mision.get("titulo_mision", "Desafío de Evolución"),
        descripcion=datos_mision.get(
            "descripcion", "Completa este hito estratégico para tu empresa."
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
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    _verificar_propietario(usuario_actual, usuario_id)
    return db.query(models.Mision).filter(models.Mision.usuario_id == usuario_id).all()


@app.put(
    "/usuarios/{usuario_id}/misiones/{mision_id}/completar",
    tags=["Gamificación"],
)
def completar_mision(
    usuario_id: int,
    mision_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    _verificar_propietario(usuario_actual, usuario_id)

    mision = (
        db.query(models.Mision)
        .filter(
            models.Mision.id == mision_id,
            models.Mision.usuario_id == usuario_id,
        )
        .first()
    )

    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    if mision.estado == "completada":
        return {"mensaje": "La misión ya estaba completada", "mision": mision}

    mision.estado = "completada"

    db_usuario = (
        db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    )
    if db_usuario and db_usuario.pasaporte:
        db_usuario.pasaporte.puntos_experiencia += mision.recompensa_puntos
        if db_usuario.arbol:
            evaluar_y_actualizar_arbol(db, db_usuario.arbol, db_usuario.pasaporte)

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


@app.get("/usuarios/{usuario_id}/bio-estructura", tags=["Gamificación"])
def obtener_fase_bio_estructura(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    _verificar_propietario(usuario_actual, usuario_id)

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.arbol:
        return {
            "nivel": 1,
            "fase_actual": "🌱 Semilla",
            "estado_crecimiento": "semilla",
            "energia_vital": 100,
        }

    pasaporte = usuario.pasaporte
    nivel = pasaporte.nivel_actual if pasaporte else 1
    info = BIO_MAP.get(nivel, BIO_MAP[10])

    return {
        "nivel": nivel,
        "fase_actual": info["label"],
        "estado_crecimiento": usuario.arbol.estado_crecimiento,
        "energia_vital": usuario.arbol.energia_vital,
    }


@app.get("/usuarios/{usuario_id}/libro", tags=["Libro Vivo"])
def obtener_estado_libro_vivo(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    _verificar_propietario(usuario_actual, usuario_id)

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.libro_vivo:
        return {"capitulo_actual": 1, "paginas_completadas": 0, "resumen_adn": {}}

    return {
        "capitulo_actual": usuario.libro_vivo.capitulo_actual,
        "paginas_completadas": usuario.libro_vivo.paginas_completadas,
        "resumen_adn": usuario.libro_vivo.resumen_adn,
    }


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
    _verificar_propietario(usuario_actual, usuario_id)

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
    rol_activo = getattr(interaccion, "rol_activo", "emprendimiento")

    analisis_ia = ia_service.generar_analisis_xixi(
        mensaje_usuario=mensaje,
        estado_arbol=estado_arbol,
        nivel_usuario=nivel_usuario,
        rol_activo=rol_activo,
    )

    xp_ganado = analisis_ia.get("xp_ganado", 5)
    energia_ganada = analisis_ia.get("energia_ganada", 2)
    respuesta_xixi = analisis_ia.get("respuesta_guia", "XiXi está contigo.")

    interaccion.respuesta_guia = respuesta_xixi
    nueva_interaccion = crud.registrar_interaccion(
        db=db,
        usuario_id=usuario_id,
        interaccion=interaccion,
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
    usuario_id: int,
    xp_ganado: int,
    db: Session = Depends(get_db),
):
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
        "mensaje": "Evolución procesada con éxito.",
        "xp_totales": usuario.pasaporte.puntos_experiencia,
        "nivel_actual": usuario.pasaporte.nivel_actual,
    }


@app.post("/usuarios/{usuario_id}/reset-base-cero", tags=["Dev Mode"])
def resetear_usuario_base_cero(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.pasaporte:
        usuario.pasaporte.puntos_experiencia = 0
        usuario.pasaporte.nivel_actual = 1
        usuario.pasaporte.insignias = []

    if usuario.arbol:
        usuario.arbol.estado_crecimiento = "semilla"
        usuario.arbol.energia_vital = 100

    if usuario.libro_vivo:
        usuario.libro_vivo.capitulo_actual = 1
        usuario.libro_vivo.paginas_completadas = 0
        usuario.libro_vivo.resumen_adn = {}

    db.query(models.Mision).filter(models.Mision.usuario_id == usuario_id).delete()
    db.commit()
    return {"mensaje": "Usuario reiniciado a Base Cero con éxito."}


class ADNMarcaSchema(BaseModel):
    nombre_empresa: str
    eslogan: str
    color_marca: str


@app.put("/usuarios/{usuario_id}/libro/adn", tags=["Libro Vivo"])
def actualizar_adn_marca(
    usuario_id: int,
    adn_data: ADNMarcaSchema,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    _verificar_propietario(usuario_actual, usuario_id)

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.libro_vivo:
        db_libro = models.LibroVivo(usuario_id=usuario_id)
        db.add(db_libro)
        db.commit()
        db.refresh(db_libro)
        usuario.libro_vivo = db_libro

    usuario.libro_vivo.resumen_adn = {
        "nombre_empresa": adn_data.nombre_empresa,
        "eslogan": adn_data.eslogan,
        "color_marca": adn_data.color_marca,
    }
    db.commit()
    return {
        "mensaje": "¡ADN de Marca guardado con éxito!",
        "adn": usuario.libro_vivo.resumen_adn,
    }
