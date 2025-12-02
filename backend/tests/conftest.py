"""Configuración de fixtures para tests"""

import sys
from pathlib import Path

# Agregar backend al path (ya lo tenías)
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importamos lo necesario de tu app
from database import Base, obtener_sesion
from main import app  # OJO: ahora lo importamos después de definir el path


# 1. Crear engine de pruebas (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # necesario con SQLite + FastAPI
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
)

# 2. Crear las tablas en la BD de pruebas
Base.metadata.create_all(bind=engine_test)


# 3. Override de la dependencia obtener_sesion para que use SQLite en lugar de Postgres
def override_obtener_sesion():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Registramos el override en la app
app.dependency_overrides[obtener_sesion] = override_obtener_sesion


# 4. Fixture del cliente de tests
@pytest.fixture
def client():
    """Cliente de test que usa BD de pruebas (SQLite), no Postgres real."""
    with TestClient(app) as c:
        yield c
