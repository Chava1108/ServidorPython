# Dockerfile para Railway - Python 3.11 garantizado
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Dependencias del sistema para mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear carpetas necesarias
RUN mkdir -p staticfiles

EXPOSE 8000

# Comando de inicio
CMD sh -c "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn backend_tesis.wsgi:application --bind 0.0.0.0:\$PORT --workers 2"
