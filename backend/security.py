import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

# Variables de Configuración de Seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_historias_que_inspiran_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas de vigencia

# Contexto de Hasheo con Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str) -> str:
    """Genera el hash seguro encriptado mediante bcrypt limitando el tamaño a 72 bytes."""
    # Truncado seguro UTF-8 a máximo 72 bytes
    pwd_safe = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(pwd_safe)


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    pwd_safe = plain_password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.verify(pwd_safe, hashed_password)


def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
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
