import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "vault")
DB_PASSWORD = os.getenv("DB_PASSWORD", "vaultpass")
DB_HOST = os.getenv("DB_HOST", "db")          # en Docker, 'db' está perfecto
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vaultdb")

URL_BD = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL = URL_BD  # 👈 línea nueva, por compatibilidad con lo que estábamos probando

engine = create_engine(URL_BD, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def obtener_sesion():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
