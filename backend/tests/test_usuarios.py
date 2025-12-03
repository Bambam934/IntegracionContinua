# tests/test_usuarios.py
import pytest

def test_docs_endpoint(client):
    response = client.get("/docs")
    assert response.status_code == 200

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_registro_usuario(client):
    response = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Juan",
            "apellido": "Pérez",
            "correo": "juan@example.com",
            "contrasena": "password123"
        }
    )
    # Cambiar de 200 a 201 (Created)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["correo"] == "juan@example.com"

def test_registro_usuario_correo_duplicado(client):
    # Primer registro
    client.post(
        "/usuarios/registro",
        json={
            "nombre": "Ana",
            "apellido": "García",
            "correo": "ana@example.com",
            "contrasena": "password123"
        }
    )
    
    # Segundo registro con mismo correo
    response = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Ana",
            "apellido": "García",
            "correo": "ana@example.com",
            "contrasena": "password456"
        }
    )
    
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"].lower()

def test_registro_usuario_datos_incompletos(client):
    response = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Incompleto",
            # Falta apellido, correo y contraseña
        }
    )
    assert response.status_code == 422  # Unprocessable Entity

def test_registro_usuario_correo_invalido(client):
    response = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Test",
            "apellido": "User",
            "correo": "correo-invalido",
            "contrasena": "password123"
        }
    )
    assert response.status_code == 422