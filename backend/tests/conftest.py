# tests/conftest.py
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

# Establecer entorno de prueba
os.environ["TESTING"] = "true"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from fastapi.testclient import TestClient

# Configurar SQLite para pruebas
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    """Fixture para el motor de base de datos."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    
    # IMPORTANTE: En Windows, necesitamos disposar el motor
    # para liberar el archivo de la base de datos
    engine.dispose()
    
    # Esperar un momento para que Windows libere el archivo
    import time
    time.sleep(0.1)
    
    # Intentar eliminar el archivo, pero no fallar si no se puede
    try:
        if os.path.exists("test.db"):
            os.remove("test.db")
    except PermissionError:
        print("⚠️ No se pudo eliminar test.db (puede estar bloqueado por Windows)")

@pytest.fixture
def db_session(engine):
    """Fixture para sesiones de base de datos."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Fixture para el cliente de pruebas."""
    # Sobrescribir la dependencia de la base de datos
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar las dependencias sobrescritas
    app.dependency_overrides.clear()