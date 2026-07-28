"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / API
Servidor Principal FastAPI - Endpoints del Ecosistema
===============================================================================
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from . import models
from . import schemas
from .database import engine
from . import crud
import database
import security
import ia_service
import pdf_service

# Crear tablas en la base de datos de manera automática
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Historias que Inspiran® - API Core",
    description="Backend oficial del ecosistema de aprendizaje, mentoría e IA",
    version="1.0.0",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def estado_api():
    """Endpoint de salud del sistema."""
    return {
        "sistema": "Historias que Inspiran® API",
        "estado": "Operativo",
        "version": "1.0.0",
    }


# -----------------------------------------------------------------------------
# Autenticación de Usuarios
# -----------------------------------------------------------------------------
@app.post(
    "/auth/registro",
    response_model=schemas.UsuarioOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_usuario(
    usuario: schemas.UsuarioCrear, db: Session = Depends(database.get_db)
):
    db_usuario = crud.obtener_usuario_por_email(db, email=usuario.email)
    if db_usuario:
        raise HTTPException(
            status_code=400, detail="El correo electrónico ya está registrado."
        )
    return crud.crear_usuario(db=db, usuario=usuario)


@app.post("/auth/login", response_model=schemas.TokenRespuesta)
def login_usuario(
    credenciales: schemas.UsuarioLogin, db: Session = Depends(database.get_db)
):
    usuario = crud.obtener_usuario_por_email(db, email=credenciales.email)
    if not usuario or not security.verificar_password(
        credenciales.password, usuario.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas."
        )
    access_token = security.crear_token_acceso(
        data={"sub": usuario.email, "id": usuario.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# -----------------------------------------------------------------------------
# Perfil y Ecosistema Gamificado
# -----------------------------------------------------------------------------
@app.get("/usuario/perfil", response_model=schemas.UsuarioOut)
def obtener_perfil(
    db: Session = Depends(database.get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    usuario = crud.obtener_usuario_por_email(db, email=usuario_actual.get("sub"))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.get("/usuario/arbol", response_model=schemas.ArbolProgresoOut)
def ver_arbol(
    db: Session = Depends(database.get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    usuario = crud.obtener_usuario_por_email(db, email=usuario_actual.get("sub"))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    arbol = crud.obtener_arbol(db, usuario_id=usuario.id)
    return arbol


@app.get("/usuario/pasaporte", response_model=schemas.PasaporteOut)
def ver_pasaporte(
    db: Session = Depends(database.get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    usuario = crud.obtener_usuario_por_email(db, email=usuario_actual.get("sub"))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    pasaporte = crud.obtener_pasaporte(db, usuario_id=usuario.id)
    return pasaporte


@app.get("/usuario/libro", response_model=schemas.LibroVivoOut)
def ver_libro_vivo(
    db: Session = Depends(database.get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    usuario = crud.obtener_usuario_por_email(db, email=usuario_actual.get("sub"))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    libro = crud.obtener_libro_vivo(db, usuario_id=usuario.id)
    return libro


# -----------------------------------------------------------------------------
# Motor IA Copiloto
# -----------------------------------------------------------------------------
@app.post("/ia/generar-capitulo", response_model=schemas.GenerarHistoriaResponse)
def generar_capitulo(
    solicitud: schemas.GenerarHistoriaRequest,
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
    db: Session = Depends(database.get_db),
):
    # 1. Obtener y validar el usuario
    usuario = crud.obtener_usuario_por_email(db, email=usuario_actual.get("sub"))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 2. Generar la historia con el servicio de IA
    resultado = ia_service.generar_capitulo_narrativo(
        capitulo=solicitud.capitulo, respuestas=solicitud.respuestas_usuario
    )

    # 3. Guardar en la base de datos (Libro Vivo)
    crud.actualizar_libro_vivo(
        db=db,
        usuario_id=usuario.id,
        nuevo_capitulo={
            "capitulo": solicitud.capitulo,
            "narrativa": resultado["historia_narrativa"],
        },
        resumen_adn=solicitud.respuestas_usuario,
    )

    # 4. Otorgar recompensas en el Pasaporte y Árbol de Progreso
    puntos = resultado.get("puntos_otorgados", 50)
    crud.otorgar_recompensas_capitulo(db=db, usuario_id=usuario.id, puntos_xp=puntos)

    # 5. RETORNO OBLIGATORIO: Garantizar que se devuelva el diccionario resultado
    return resultado


@app.post("/ia/conversar")
def conversar_personaje(
    solicitud: schemas.MensajeChat,
    db: Session = Depends(database.get_db),
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
):
    respuesta = ia_service.conversar_con_personaje(
        personaje=solicitud.personaje,
        mensaje_usuario=solicitud.mensaje,
        contexto_usuario={"email": usuario_actual.get("sub")},
    )

    return {"personaje": solicitud.personaje, "respuesta": respuesta}


from fastapi.responses import StreamingResponse
import pdf_service


@app.get("/usuario/libro/pdf")
def descargar_pdf_libro(
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
    db: Session = Depends(database.get_db),
):
    usuario = crud.obtener_usuario_por_email(db, email=usuario_actual.get("sub"))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    libro = crud.obtener_libro_vivo(db, usuario.id)
    pasaporte = crud.obtener_pasaporte(db, usuario.id)

    datos_libro = {
        "capitulos_narrativos": libro.capitulos_narrativos if libro else [],
        "resumen_adn": libro.resumen_adn if libro else {},
    }

    datos_pasaporte = {
        "nivel_actual": pasaporte.nivel_actual if pasaporte else 1,
        "puntos_experiencia": pasaporte.puntos_experiencia if pasaporte else 0,
    }

    pdf_buffer = pdf_service.generar_pdf_libro_vivo(
        nombre_usuario=usuario.nombre,
        datos_libro=datos_libro,
        datos_pasaporte=datos_pasaporte,
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Libro_Vivo_{usuario.nombre}.pdf"
        },
    )


@app.post("/ia/validar-mision", response_model=schemas.ValidarMisionResponse)
def validar_mision(
    solicitud: schemas.ValidarMisionRequest,
    usuario_actual: dict = Depends(security.obtener_usuario_actual),
    db: Session = Depends(database.get_db),
):
    usuario = crud.obtener_usuario_por_email(db, email=usuario_actual.get("sub"))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 1. Evaluar respuesta con IA
    resultado = ia_service.evaluar_mision_usuario(
        mision=solicitud.mision, respuesta_usuario=solicitud.respuesta_usuario
    )

    # 2. Otorgar recompensas extra
    if resultado.get("cumplida", True):
        crud.otorgar_recompensas_capitulo(
            db=db,
            usuario_id=usuario.id,
            puntos_xp=resultado.get("puntos_otorgados", 30),
        )

    return resultado
