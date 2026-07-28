"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / API
Conexión de Base de Datos y Gestión de Sesiones ORM
===============================================================================
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./historias_genesis.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Inyector de dependencia para abrir y cerrar sesiones de BD por cada request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
