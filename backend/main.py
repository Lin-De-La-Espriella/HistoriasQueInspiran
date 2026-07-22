from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# Crea automáticamente las tablas en PostgreSQL si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Historias que Inspiran API",
    description="Motor principal de la plataforma EdTech",
    version="0.0.1",
)


@app.get("/")
def ruta_principal():
    return {
        "estado": "En línea",
        "mensaje": "El cerebro de Historias que Inspiran está funcionando y conectado a PostgreSQL.",
    }


# Endpoint para verificar la conexión a la Base de Datos
@app.get("/test-db")
def probar_conexion_db(db: Session = Depends(get_db)):
    # Ejecutamos una consulta simple para validar la conexión viva
    return {"conexion_db": "Exitosa", "motor": "PostgreSQL 16 en Docker"}
