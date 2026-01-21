# backend/Dockerfile
FROM python:3.11-slim

# Evita archivos basura de python y fuerza logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos herramientas básicas de sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 1. Copiamos SOLO los requerimientos primero (para caché)
COPY requirements.txt .

# 2. Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos el resto del código
COPY . .

# Exponemos puerto
EXPOSE 8000

# Comando por defecto (docker-compose lo sobrescribirá para desarrollo)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]