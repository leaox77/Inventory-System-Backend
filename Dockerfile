FROM python:3.13-slim-bookworm

# Establecer directorio de trabajo
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalar dependencias del sistema necesarias (incluye soporte para reportlab)
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
