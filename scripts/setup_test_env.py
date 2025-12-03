#!/usr/bin/env python3
"""
Script para configurar el entorno de pruebas.
"""
import os
import sys

def setup_test_environment():
    """Configurar el entorno para pruebas."""
    # Establecer variables de entorno para pruebas
    os.environ["TESTING"] = "true"
    os.environ["SECRET_KEY"] = "test-secret-key-for-ci-cd-pipeline"
    os.environ["FERNET_KEY"] = "test-fernet-key-32-bytes-123456789012"
    
    # Agregar el directorio raíz al path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    
    print("✅ Entorno de pruebas configurado")
    print(f"📁 Directorio raíz: {root_dir}")
    print(f"🐍 Python path: {sys.path}")

if __name__ == "__main__":
    setup_test_environment()