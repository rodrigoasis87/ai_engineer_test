# frontend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 1. Copiamos requirements
COPY requirements.txt .

# 2. Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos código
COPY . .

# Exponemos puerto de Streamlit
EXPOSE 8501

# Chequeo de salud para saber si Streamlit arrancó
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando de inicio
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]