from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión al contenedor Docker: postgresql://usuario:contraseña@localhost:puerto/nombre_bd
SQLALCHEMY_DATABASE_URL = (
    "postgresql://admin:super_password_seguro@localhost:5432/historias_inspiran"
)

# Crear el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la sesión de base de datos para las peticiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para nuestros modelos
Base = declarative_base()


# Función para obtener la sesión de BD en cada endpoint (Inyección de dependencias)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
