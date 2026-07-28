import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

# -----------------------------------------------------------------------------
# Configuración del Path y Carga de Variables de Entorno (.env)
# -----------------------------------------------------------------------------
# Incluye la carpeta 'apps/api' en el PATH para importar los módulos locales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Cargar el archivo .env ubicado en apps/api/.env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -----------------------------------------------------------------------------
# Configuración de Alembic
# -----------------------------------------------------------------------------
config = context.config

# Interpretar el archivo de configuración para los loggers de Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inyectar la URL de la base de datos desde el .env al objeto Config de Alembic
db_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
config.set_main_option("sqlalchemy.url", db_url)

# -----------------------------------------------------------------------------
# Importación de Modelos de SQLAlchemy para Autogeneración
# -----------------------------------------------------------------------------
import models  # Carga models.py de la API

target_metadata = models.Base.metadata


# -----------------------------------------------------------------------------
# Funciones de Ejecución de Migraciones
# -----------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline' sin abrir una conexión directa."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online' creando el Engine de SQLAlchemy."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
