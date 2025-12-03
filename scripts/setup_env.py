#!/usr/bin/env python3
"""
Script to generate environment variables.
"""
import secrets
from cryptography.fernet import Fernet

def generate_env_file():
    """Generate .env file with random secrets."""
    print("🔐 Generating environment variables...")
    
    secret_key = secrets.token_urlsafe(32)
    fernet_key = Fernet.generate_key().decode()
    
    env_content = f"""# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vault_db
DB_USER=vault_user
DB_PASSWORD=vault_password

# Application
SECRET_KEY={secret_key}
FERNET_KEY={fernet_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Python
PYTHONPATH=./backend
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created")
    print("📋 Copy these to GitHub Secrets if needed:")

if __name__ == "__main__":
    generate_env_file()