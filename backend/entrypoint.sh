#!/bin/bash
set -e

# Agrega /app al PYTHONPATH
export PYTHONPATH="/app:$PYTHONPATH"

# Ejecuta el servidor
exec uvicorn main:app --host 0.0.0.0 --port 5000