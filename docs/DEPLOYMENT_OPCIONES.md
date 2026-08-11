# 🚀 Guía de Deployment - POOGraph en Internet

## 📋 Tabla de Contenidos

1. [Opciones de Hosting](#opciones-de-hosting)
2. [Recomendación para Proyecto Educativo](#recomendación-para-proyecto-educativo)
3. [Opción 1: Azure (Recomendado para UAA)](#opción-1-azure-recomendado-para-uaa)
4. [Opción 2: Railway (Más Fácil)](#opción-2-railway-más-fácil)
5. [Opción 3: DigitalOcean (Profesional)](#opción-3-digitalocean-profesional)
6. [Opción 4: Render (Gratis con limitaciones)](#opción-4-render-gratis-con-limitaciones)
7. [Configuración de Dominio](#configuración-de-dominio)
8. [Checklist Pre-Deployment](#checklist-pre-deployment)
9. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## 🎯 Opciones de Hosting

### Comparativa Rápida

| Servicio | Frontend | Backend | Base de Datos | Precio Mensual | Dificultad | Uptime |
|----------|----------|---------|---------------|----------------|------------|--------|
| **Azure** | ✅ | ✅ | ✅ | $0-50 (Edu) | ⭐⭐⭐ | 99.9% |
| **Railway** | ✅ | ✅ | ✅ | $5-20 | ⭐⭐ | 99.9% |
| **Render** | ✅ | ✅ | ✅ | $0-25 | ⭐⭐ | 99% |
| **DigitalOcean** | ✅ | ✅ | ✅ | $12-24 | ⭐⭐⭐⭐ | 99.99% |
| **Vercel + Railway** | ✅ | ❌ | ❌ | $0-20 | ⭐ | 99.9% |
| **Heroku** | ✅ | ✅ | ✅ | $7-25 | ⭐⭐ | 99.9% |
| **AWS** | ✅ | ✅ | ✅ | $10-100+ | ⭐⭐⭐⭐⭐ | 99.99% |

**Leyenda**:
- ⭐ = Muy fácil
- ⭐⭐⭐⭐⭐ = Muy complejo

---

## 🏆 Recomendación para Proyecto Educativo

### **Opción Óptima: Azure for Students**

**¿Por qué Azure?**
1. ✅ **Créditos gratuitos**: $100 USD para estudiantes
2. ✅ **Soporte institucional**: UAA tiene convenio con Microsoft
3. ✅ **Documentación extensa**: En español
4. ✅ **Escalable**: Si el proyecto crece
5. ✅ **Profesional**: Prestigio para tu tesis

**Componentes en Azure**:
- **Frontend**: Azure Static Web Apps (GRATIS)
- **Backend**: Azure App Service (desde $0 con créditos)
- **Base de Datos**: Azure Database for MySQL (desde $0 con créditos)

**Costo Estimado con Créditos Estudiantiles**: **$0-20/mes**

---

### **Opción Alternativa: Railway (La Más Fácil)**

**¿Por qué Railway?**
1. ✅ **Súper fácil**: Deploy con un clic
2. ✅ **Todo integrado**: Frontend, backend, DB en un lugar
3. ✅ **Plan gratis inicial**: $5 de crédito gratis
4. ✅ **GitHub integration**: Auto-deploy en cada push

**Costo Estimado**: **$5-15/mes**

---

## 🔷 Opción 1: Azure (Recomendado para UAA)

### Paso 1: Obtener Créditos de Estudiante

1. Ir a: https://azure.microsoft.com/es-mx/free/students/
2. Registrarse con tu correo institucional UAA (@edu.uaa.mx)
3. Verificar con tu credencial de estudiante
4. Obtener **$100 USD de crédito gratis**

### Paso 2: Crear Recursos en Azure

#### A. Base de Datos MySQL

```bash
# Desde Azure Portal o Azure CLI
az mysql flexible-server create \
  --resource-group poograph-rg \
  --name poograph-mysql \
  --location eastus \
  --admin-user adminuser \
  --admin-password "TuPassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 8.0.21 \
  --storage-size 32
```

**Configuración en Portal**:
1. Ir a **Azure Portal** → **Create a resource**
2. Buscar **Azure Database for MySQL flexible server**
3. Configurar:
   - **Server name**: poograph-mysql
   - **Region**: East US (más barato)
   - **Compute + storage**: B1ms (Burstable, ~$15/mes)
   - **Admin username**: adminuser
   - **Password**: [Tu contraseña segura]
4. En **Networking**:
   - ✅ Allow public access from Azure services
   - ✅ Add current client IP address
5. **Create**

#### B. Backend (Azure App Service)

```bash
# Crear App Service Plan
az appservice plan create \
  --name poograph-plan \
  --resource-group poograph-rg \
  --sku B1 \
  --is-linux

# Crear Web App para Django
az webapp create \
  --name poograph-backend \
  --resource-group poograph-rg \
  --plan poograph-plan \
  --runtime "PYTHON:3.9"
```

**Configuración Manual**:
1. **Azure Portal** → **App Services** → **Create**
2. Configurar:
   - **Name**: poograph-backend
   - **Runtime stack**: Python 3.9
   - **Region**: East US
   - **Pricing plan**: B1 Basic (~$13/mes)
3. **Create**

**Deployment del Backend**:

```bash
# En tu proyecto local
cd backend_tesis

# Instalar Azure CLI
# Windows: https://aka.ms/installazurecliwindows

# Login
az login

# Configurar deployment
az webapp deployment source config-zip \
  --resource-group poograph-rg \
  --name poograph-backend \
  --src backend.zip
```

**Configurar Variables de Entorno**:
```bash
az webapp config appsettings set \
  --resource-group poograph-rg \
  --name poograph-backend \
  --settings \
    DB_HOST="poograph-mysql.mysql.database.azure.com" \
    DB_NAME="clases" \
    DB_USER="adminuser" \
    DB_PASSWORD="TuPassword123!" \
    DJANGO_SECRET_KEY="tu-secret-key-super-segura" \
    ALLOWED_HOSTS="poograph-backend.azurewebsites.net"
```

#### C. Frontend (Azure Static Web Apps)

```bash
# Crear Static Web App
az staticwebapp create \
  --name poograph-frontend \
  --resource-group poograph-rg \
  --location eastus2
```

**Configuración Manual**:
1. **Azure Portal** → **Static Web Apps** → **Create**
2. Configurar:
   - **Name**: poograph-frontend
   - **Region**: East US 2
   - **Deployment source**: GitHub
   - **Repository**: [Tu repo]
   - **Branch**: main
   - **Build preset**: Angular
   - **App location**: /frontend
   - **Output location**: dist/tesis
3. **Create**

**Azure creará automáticamente un GitHub Action** para deploy

### Paso 3: Configurar CORS y Conexiones

En `backend_tesis/settings.py`:
```python
ALLOWED_HOSTS = [
    'poograph-backend.azurewebsites.net',
    'poograph-frontend.azurewebsites.net'
]

CORS_ALLOWED_ORIGINS = [
    'https://poograph-frontend.azurewebsites.net',
]

# Azure MySQL Connection
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '3306',
        'OPTIONS': {
            'ssl': {'ca': '/path/to/BaltimoreCyberTrustRoot.crt.pem'}
        }
    }
}
```

### Paso 4: Migrar Base de Datos

```bash
# Conectar a MySQL en Azure
mysql -h poograph-mysql.mysql.database.azure.com \
      -u adminuser \
      -p

# Crear base de datos
CREATE DATABASE clases CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Importar schema (si tienes un dump)
mysql -h poograph-mysql.mysql.database.azure.com \
      -u adminuser \
      -p clases < schema.sql
```

### Costos Estimados Azure

| Recurso | Tier | Costo Mensual |
|---------|------|---------------|
| MySQL Flexible Server | B1ms | ~$15 |
| App Service (Backend) | B1 | ~$13 |
| Static Web App (Frontend) | Free | $0 |
| **Total** | | **~$28/mes** |
| **Con créditos de estudiante** | | **$0 por 3-4 meses** |

---

## 🚂 Opción 2: Railway (Más Fácil)

### Ventajas
- ✅ Deploy en 5 minutos
- ✅ No necesitas configurar nada
- ✅ Auto-deploy desde GitHub
- ✅ $5 gratis al inicio

### Paso 1: Crear Cuenta

1. Ir a https://railway.app/
2. Sign up con GitHub
3. Vincular tu repositorio

### Paso 2: Deploy Backend

1. **New Project** → **Deploy from GitHub repo**
2. Seleccionar tu repositorio
3. Railway detectará automáticamente que es Django
4. Agregar variables de entorno:
   ```
   DB_HOST=${{MySQL.HOST}}
   DB_PORT=${{MySQL.PORT}}
   DB_NAME=${{MySQL.DATABASE}}
   DB_USER=${{MySQL.USER}}
   DB_PASSWORD=${{MySQL.PASSWORD}}
   DJANGO_SECRET_KEY=tu-secret-key
   ```

### Paso 3: Agregar MySQL

1. En tu proyecto, clic en **New**
2. Seleccionar **Database** → **MySQL**
3. Railway creará automáticamente la BD y te dará las credenciales

### Paso 4: Deploy Frontend

1. **New Service** → **GitHub Repo** (mismo repo)
2. Configurar:
   - **Root Directory**: /frontend
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: (Railway lo detecta automáticamente con nginx)

### Paso 5: Configurar Dominio

1. En el servicio de Frontend, ir a **Settings** → **Networking**
2. Clic en **Generate Domain**
3. Obtendrás algo como: `poograph.up.railway.app`

### Configurar CORS

En `backend_tesis/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'https://poograph.up.railway.app',
]
```

### Costos Estimados Railway

| Recurso | Uso | Costo Mensual |
|---------|-----|---------------|
| Backend (512MB RAM) | Always on | ~$5 |
| Frontend (256MB RAM) | Always on | ~$3 |
| MySQL (1GB) | Siempre activo | ~$5 |
| **Total** | | **~$13/mes** |
| **Con $5 gratis** | | **$8/mes** |

---

## 💧 Opción 3: DigitalOcean (Profesional)

### Ventajas
- ✅ Muy estable (99.99% uptime)
- ✅ Control total (VPS)
- ✅ Buenos precios
- ✅ Documentación excelente

### Droplet (VPS) + Docker

**Costo**: $12/mes (Droplet básico 2GB RAM)

### Paso 1: Crear Droplet

1. Ir a https://www.digitalocean.com/
2. **Create** → **Droplets**
3. Configurar:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic $12/mes (2GB RAM, 50GB SSD)
   - **Datacenter**: New York o San Francisco
   - **Authentication**: SSH keys (recomendado)
4. **Create Droplet**

### Paso 2: Configurar Servidor

```bash
# SSH al servidor
ssh root@tu-ip-del-droplet

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Instalar Git
apt install git -y
```

### Paso 3: Clonar y Deploy

```bash
# Clonar repo
git clone https://github.com/tu-usuario/POOGRAPH.git
cd POOGRAPH

# Crear archivo .env
nano .env
```

**Archivo .env**:
```env
DB_NAME=clases
DB_USER=root
DB_PASSWORD=tu-password-seguro
DB_HOST=db
DJANGO_SECRET_KEY=tu-secret-key-muy-largo
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

**Actualizar docker-compose.yml para producción**:
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - poograph-network

  backend:
    build: ./backend_tesis
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    depends_on:
      - db
    networks:
      - poograph-network

  frontend:
    build: ./frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - poograph-network

volumes:
  mysql_data:

networks:
  poograph-network:
    driver: bridge
```

```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### Paso 4: Configurar Nginx y SSL

```bash
# Instalar Certbot (Let's Encrypt)
apt install certbot python3-certbot-nginx -y

# Configurar Nginx
nano /etc/nginx/sites-available/poograph
```

**Configuración Nginx**:
```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Activar sitio
ln -s /etc/nginx/sites-available/poograph /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Obtener SSL gratis
certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

---

## 🎨 Opción 4: Render (Gratis con Limitaciones)

### Ventajas
- ✅ Plan gratuito disponible
- ✅ Muy fácil de usar
- ✅ Auto-deploy desde GitHub
- ⚠️ Limitación: Se duerme después de 15 min de inactividad

### Plan Gratis:
- Backend: 512MB RAM, se duerme si no hay tráfico
- Base de Datos: PostgreSQL gratis (necesitarías migrar de MySQL)
- Frontend: Gratis

**Costo**: $0/mes (con limitaciones) o $7-20/mes (sin limitaciones)

### Pasos:

1. Ir a https://render.com/
2. **New** → **Web Service** (Backend)
3. Conectar GitHub
4. Configurar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend_tesis.wsgi:application`
5. **New** → **Static Site** (Frontend)
6. Configurar:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist/tesis`

---

## 🌐 Configuración de Dominio

### Opciones de Dominio

1. **Dominio Gratis (Subdominio)**:
   - Railway: `tu-app.up.railway.app`
   - Azure: `tu-app.azurewebsites.net`
   - Render: `tu-app.onrender.com`

2. **Dominio Personalizado** ($10-15/año):
   - Namecheap: https://www.namecheap.com/
   - GoDaddy: https://www.godaddy.com/
   - Google Domains: https://domains.google/

### Configurar DNS

Si compras `poograph.com`:

**Registros DNS**:
```
A Record:
  Host: @
  Value: [IP de tu servidor]

CNAME Record:
  Host: www
  Value: poograph.com

CNAME Record:
  Host: api
  Value: [URL de tu backend]
```

---

## ✅ Checklist Pre-Deployment

### Backend Django

- [ ] `DEBUG = False` en settings.py
- [ ] `ALLOWED_HOSTS` configurado
- [ ] `SECRET_KEY` en variable de entorno
- [ ] `CORS_ALLOWED_ORIGINS` configurado
- [ ] `requirements.txt` actualizado
- [ ] Migraciones aplicadas
- [ ] `collectstatic` ejecutado
- [ ] Gunicorn configurado

### Frontend Angular

- [ ] `environment.prod.ts` con URL correcta del backend
- [ ] Build de producción testeado localmente
- [ ] Rutas configuradas correctamente
- [ ] SSL/HTTPS habilitado

### Base de Datos

- [ ] Backup creado
- [ ] Schema importado
- [ ] Usuario con permisos correctos
- [ ] Conexión SSL habilitada
- [ ] Firewall configurado

### Seguridad

- [ ] SSL/HTTPS configurado
- [ ] Contraseñas fuertes
- [ ] CORS restrictivo
- [ ] Rate limiting configurado
- [ ] Logs de seguridad activados

---

## 📊 Monitoreo y Mantenimiento

### Herramientas de Monitoreo (Gratis)

1. **UptimeRobot**: https://uptimerobot.com/
   - Monitoreo de uptime
   - Alertas por email
   - 50 monitores gratis

2. **Google Analytics**:
   - Tráfico de usuarios
   - Estadísticas de uso

3. **Sentry**: https://sentry.io/
   - Tracking de errores
   - Plan gratis: 5K eventos/mes

### Backups

**Azure**:
```bash
# Backup automático de MySQL
az mysql flexible-server backup list \
  --resource-group poograph-rg \
  --server-name poograph-mysql
```

**DigitalOcean**:
```bash
# Backup manual de MySQL
docker exec mysql mysqldump -u root -p clases > backup_$(date +%Y%m%d).sql

# Subir a cloud storage
# O configurar backup automático con cron
```

---

## 💡 Recomendación Final

### Para tu Tesis (UAA):

**Opción 1: Azure for Students** ⭐⭐⭐⭐⭐
- Profesional
- Gratis con créditos
- Respaldo institucional
- Escalable

### Si Buscas Facilidad:

**Opción 2: Railway** ⭐⭐⭐⭐
- Súper fácil
- Deploy en minutos
- Económico

### Si Necesitas Control Total:

**Opción 3: DigitalOcean** ⭐⭐⭐⭐
- Control completo
- Buena relación precio/calidad
- Estable

---

## 📞 Siguiente Paso

¿Qué opción prefieres? Te puedo ayudar con la configuración paso a paso de cualquiera de ellas.

**Recomiendo empezar con Azure** dado que:
1. Es gratis con tus créditos de estudiante UAA
2. Profesional para tu tesis
3. Puedo guiarte en cada paso

¿Quieres que hagamos el deployment en Azure? 🚀

