from fastapi import FastAPI

# Inicializamos el núcleo de la aplicación
app = FastAPI(
    title="Historias que Inspiran API",
    description="Motor principal de la plataforma EdTech",
    version="0.0.1",
)


# Creamos nuestra primera ruta (Endpoint)
@app.get("/")
def ruta_principal():
    return {
        "estado": "En línea",
        "mensaje": "El cerebro de Historias que Inspiran está funcionando perfectamente. ¡Hola, Rafael!",
    }
