# backend/Dockerfile - Versión mejorada
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y otras bibliotecas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Puerto expuesto
EXPOSE 5000

# Salud de la aplicación
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando para ejecutar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]