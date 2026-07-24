import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from . import schemas

# Configuración de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta local para firmar los Tokens JWT (0 costo)
SECRET_KEY = os.getenv(
    "SECRET_KEY", "super_clave_secreta_local_historias_inspiran_2026"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # El token durará 24 horas


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash guardado."""
    return pwd_context.verify(plain_password, hashed_password)


def obtener_password_hash(password: str) -> str:
    """Convierte una contraseña en texto plano a un Hash irrecuperable encriptado."""
    return pwd_context.hash(password)


def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un Token JWT firmado para el usuario que inicia sesión."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    token_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# Define de dónde extraerá FastAPI el token Bearer (del endpoint /token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Middleware/Dependencia para validar el Token JWT en endpoints protegidos.
    Extrae la identidad del usuario y sus permisos (rol).
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de acceso.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodificar el Token usando nuestra clave secreta local
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        usuario_id: int = payload.get("usuario_id")
        rol: str = payload.get("rol")

        if email is None or usuario_id is None:
            raise credenciales_exception

        return {"email": email, "usuario_id": usuario_id, "rol": rol}

    except JWTError:
        raise credenciales_exception
