import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. Mapeo Lógico de la Ruta
# Obtenemos la ruta absoluta de la carpeta donde está este archivo (backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")

# 2. Cargar variables forzando la lectura en la ruta específica
load_dotenv(dotenv_path=env_path)

# Obtener URL de conexión desde el entorno (Local o Supabase Cloud)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:super_password_seguro@localhost:5432/historias_inspiran",
)

# Ajuste necesario para URLs de Supabase/Heroku (postgres:// -> postgresql://)
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
