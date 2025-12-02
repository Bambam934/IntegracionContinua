from fastapi import FastAPI
from database import Base, engine 
from rutas import usuarios, credenciales
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestor de Contraseñas - Backend en Español")
app.include_router(usuarios.router)
app.include_router(credenciales.router)

@app.get("/health")
def health():
    return {"status": "ok"}