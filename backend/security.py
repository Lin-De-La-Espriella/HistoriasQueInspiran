import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt  # <-- Importación directa de la librería nativa

load_dotenv()

# Variables de Configuración de Seguridad
SECRET_KEY = os.getenv(
    "SECRET_KEY", "super_secret_key_historias_que_inspiran_2026"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas de vigencia

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña usando bcrypt nativo de forma limpia."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Genera el hash seguro usando bcrypt nativo, sin intermediarios."""
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')


def crear_token_acceso(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Genera un Token JWT firmado con expiration claim."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    """Decodifica el Token JWT en rutas protegidas para validar autenticación."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de acceso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception