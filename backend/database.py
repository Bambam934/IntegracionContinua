# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Diferentes URLs para diferentes entornos
if os.getenv("TESTING", "false").lower() == "true":
    # SQLite para pruebas (no necesita servidor)
    DATABASE_URL = "sqlite:///./test.db"
else:
    # PostgreSQL para desarrollo/producción
    DB_USER = os.getenv("DB_USER", "vault_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "vault_password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "vault_db")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Para SQLite, necesitamos configuraciones especiales
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


obtener_sesion = get_db
# Alias para compatibilidad con el código existente
obtener_sesion = get_db
