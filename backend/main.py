# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import Base, engine 
from rutas import usuarios, credenciales
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crear tablas
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: limpiar si es necesario
    # engine.dispose()  # Opcional: cerrar conexiones

app = FastAPI(
    title="Gestor de Contraseñas - Backend en Español",
    lifespan=lifespan
)

app.include_router(usuarios.router)
app.include_router(credenciales.router)

@app.get("/health")
def health():
    return {"status": "ok"}