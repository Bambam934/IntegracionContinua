"""Tests para el módulo de usuarios"""
import uuid
import pytest

def test_docs_endpoint(client):
    """Test que la documentación está disponible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_health_check(client):
    """Test básico de que la API responde"""
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_registro_usuario(client):
    """Test básico de registro de usuario"""
    email_unico = f"test-{uuid.uuid4()}@example.com"
    
    response = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Test",
            "apellido": "User",
            "correo": email_unico,
            "contrasena": "test1234"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Test"
    assert data["correo"] == email_unico
    assert "id" in data

def test_registro_usuario_correo_duplicado(client):
    """Test que no permite registrar dos usuarios con el mismo correo"""
    email = f"test-{uuid.uuid4()}@example.com"
    
    # Primer registro - debe funcionar
    response1 = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Test1",
            "apellido": "User1",
            "correo": email,
            "contrasena": "test1234"
        }
    )
    assert response1.status_code == 201
    
    # Segundo registro con mismo email - debe fallar
    response2 = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Test2",
            "apellido": "User2",
            "correo": email,
            "contrasena": "test1234"
        }
    )
    assert response2.status_code == 400
    assert "ya está registrado" in response2.json()["detail"]

def test_registro_usuario_datos_incompletos(client):
    """Test que valida campos requeridos"""
    # Falta nombre
    response = client.post(
        "/usuarios/registro",
        json={
            "apellido": "User",
            "correo": f"test-{uuid.uuid4()}@example.com",
            "contrasena": "test1234"
        }
    )
    assert response.status_code == 422  




def test_registro_usuario_correo_invalido(client):
    """
    Verifica que el backend rechaza el registro
    cuando el correo NO tiene un formato válido.
    """
    response = client.post(
        "/usuarios/registro",
        json={
            "nombre": "Usuario Correo Malo",
            "correo": "no-es-un-correo-valido",
            "contrasena": "Password123!"
        },
    )

    assert response.status_code == 422

    data = response.json()
    assert "detail" in data
    assert any(
        err.get("loc", [None])[-1] == "correo"
        for err in data.get("detail", [])
    )