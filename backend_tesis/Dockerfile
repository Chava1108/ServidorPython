# ============================================================
# Dockerfile — Backend Django (POOGraph)
# ============================================================
# Imagen base con Python 3.11 + herramientas de compilación
FROM python:3.11-slim

# Evitar prompts interactivos y configurar encoding
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# Instalar dependencias del sistema:
#   - default-libmysqlclient-dev: para mysqlclient (conector MySQL)
#   - default-jdk: Java (compilación de código del alumno)
#   - g++: C++ (compilación de código del alumno)
#   - pkg-config: requerido por mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    default-jdk \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias de Python primero (cache de capas)
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copiar el código fuente del proyecto
COPY . .

# Crear carpetas necesarias si no existen
RUN mkdir -p codigos_fuente datos archivos

# Puerto del servidor Django
EXPOSE 8000

# Comando de inicio: runserver para desarrollo
# En producción cambiar por gunicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
