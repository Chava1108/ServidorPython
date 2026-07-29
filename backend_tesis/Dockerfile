# ============================================================
# Dockerfile — Backend Django (POOGraph - Producción / Railway)
# ============================================================
# Imagen base con Python 3.11 + herramientas de compilación
FROM python:3.11-slim

# Evitar prompts interactivos y configurar encoding
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PORT=8000

# Paquetes del sistema necesarios:
#   - default-libmysqlclient-dev / pkg-config: para mysqlclient
#   - default-jdk: Java (compilación de código de alumnos)
#   - g++: C++ (compilación de código de alumnos)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    default-jdk \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias de Python primero (cache de capas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente del proyecto
COPY . .

# Crear carpetas necesarias para la persistencia de datos
RUN mkdir -p codigos_fuente datos archivos staticfiles

# Recolectar archivos estáticos durante el build
RUN python manage.py collectstatic --noinput

# Expone el puerto por defecto (Railway usará la variable $PORT)
EXPOSE 8000

# Comando de inicio: migrar DB y ejecutar gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn backend_tesis.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2"]