import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Datos de conexión tomados de tu database.py
DB_NAME = "historias_inspiran"
DB_USER = "admin"
DB_PASS = "super_password_seguro"
DB_HOST = "localhost"
DB_PORT = "5432"


def resetear_base_de_datos():
    print("🔄 Conectando a PostgreSQL...")
    try:
        # 1. Conectarse a la base de datos por defecto 'postgres'
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 2. Cerrar conexiones activas a 'historias_inspiran' para evitar bloqueos
        print(f"🔒 Cerrando conexiones activas en '{DB_NAME}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{DB_NAME}'
            AND pid <> pg_backend_pid();
        """)

        # 3. Eliminar la base de datos previa
        print(f"🗑️ Eliminando base de datos '{DB_NAME}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")

        # 4. Crear la base de datos totalmente vacía
        print(f"✨ Creando base de datos limpia '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};")

        cursor.close()
        conn.close()
        print("✅ ¡Base de datos recreada con éxito!")

    except Exception as e:
        print(f"❌ Error al resetear la base de datos: {e}")


if __name__ == "__main__":
    resetear_base_de_datos()
