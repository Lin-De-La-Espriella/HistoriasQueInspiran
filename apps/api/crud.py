"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / API
Capa de Acceso a Datos (CRUD) y Gamificación
===============================================================================
"""

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import models
import schemas
import security

# =============================================================================
# 1. GESTIÓN DE USUARIOS
# =============================================================================


def obtener_usuario_por_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico."""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    """
    Crea un usuario nuevo y al mismo tiempo inicializa su ecosistema:
    Pasaporte, Árbol de Progreso y Libro Vivo.
    """
    hashed_password = security.obtener_password_hash(usuario.password)

    db_usuario = models.Usuario(
        email=usuario.email, nombre=usuario.nombre, hashed_password=hashed_password
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    nuevo_pasaporte = models.Pasaporte(usuario_id=db_usuario.id)
    nuevo_arbol = models.ArbolProgreso(usuario_id=db_usuario.id)
    nuevo_libro = models.LibroVivo(usuario_id=db_usuario.id)

    db.add(nuevo_pasaporte)
    db.add(nuevo_arbol)
    db.add(nuevo_libro)
    db.commit()

    return db_usuario


# =============================================================================
# 2. LECTURA DEL ECOSISTEMA (Árbol, Pasaporte, Libro Vivo)
# =============================================================================


def obtener_pasaporte(db: Session, usuario_id: int):
    return (
        db.query(models.Pasaporte)
        .filter(models.Pasaporte.usuario_id == usuario_id)
        .first()
    )


def obtener_arbol(db: Session, usuario_id: int):
    return (
        db.query(models.ArbolProgreso)
        .filter(models.ArbolProgreso.usuario_id == usuario_id)
        .first()
    )


def obtener_libro_vivo(db: Session, usuario_id: int):
    return (
        db.query(models.LibroVivo)
        .filter(models.LibroVivo.usuario_id == usuario_id)
        .first()
    )


# =============================================================================
# 3. ACTUALIZACIÓN Y PERSISTENCIA (El Motor del Libro Vivo)
# =============================================================================


def actualizar_libro_vivo(
    db: Session, usuario_id: int, nuevo_capitulo: dict, resumen_adn: dict
):
    """
    Inyecta un nuevo capítulo forjado asegurando la inmutabilidad de JSON.
    """
    libro = obtener_libro_vivo(db, usuario_id)
    if not libro:
        return None

    # 1. Manejo Seguro de Listas JSON
    historial = list(libro.capitulos_narrativos) if libro.capitulos_narrativos else []
    historial.append(nuevo_capitulo)
    libro.capitulos_narrativos = historial

    # 2. Manejo Seguro de Diccionarios JSON
    adn = dict(libro.resumen_adn) if libro.resumen_adn else {}
    adn.update(resumen_adn)
    libro.resumen_adn = adn

    # 3. Actualizar métricas
    libro.capitulo_actual = nuevo_capitulo.get("capitulo", libro.capitulo_actual + 1)
    libro.paginas_completadas += 1

    flag_modified(libro, "capitulos_narrativos")
    flag_modified(libro, "resumen_adn")

    db.commit()
    db.refresh(libro)
    return libro


# =============================================================================
# 4. LÓGICA DE GAMIFICACIÓN Y RECOMPENSAS
# =============================================================================


def otorgar_recompensas_capitulo(db: Session, usuario_id: int, puntos_xp: int = 50):
    """
    Otorga puntos asegurando que los registros existan previamente.
    """
    # 1. Pasaporte
    pasaporte = obtener_pasaporte(db, usuario_id=usuario_id)
    if not pasaporte:
        pasaporte = models.Pasaporte(
            usuario_id=usuario_id, puntos_experiencia=0, nivel_actual=1
        )
        db.add(pasaporte)
        db.commit()
        db.refresh(pasaporte)

    pasaporte.puntos_experiencia += puntos_xp
    pasaporte.nivel_actual = (pasaporte.puntos_experiencia // 100) + 1

    # 2. Árbol de Progreso
    arbol = obtener_arbol(db, usuario_id=usuario_id)
    if not arbol:
        arbol = models.ArbolProgreso(
            usuario_id=usuario_id, energia_vital=100, estado_crecimiento="semilla"
        )
        db.add(arbol)
        db.commit()
        db.refresh(arbol)

    nueva_energia = min(100, arbol.energia_vital + 25)
    arbol.energia_vital = nueva_energia

    if pasaporte.puntos_experiencia >= 300:
        arbol.estado_crecimiento = "árbol frondoso"
    elif pasaporte.puntos_experiencia >= 100:
        arbol.estado_crecimiento = "brote"
    else:
        arbol.estado_crecimiento = "semilla"

    db.commit()
    return {
        "puntos_ganados": puntos_xp,
        "nuevo_nivel": pasaporte.nivel_actual,
    }
