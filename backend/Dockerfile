FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

COPY . ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Establecer PYTHONPATH en el entorno
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]