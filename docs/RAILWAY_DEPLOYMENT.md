# 🚂 Guía Paso a Paso: Deploy de POOGraph en Railway

## 🎯 ¿Por Qué Railway?

- ✅ **Súper fácil** - Deploy en 10 minutos
- ✅ **Económico** - ~$10-15/mes (mucho más barato que Azure)
- ✅ **$5 gratis** al inicio
- ✅ **Auto-deploy** desde GitHub
- ✅ **Todo integrado** - No necesitas configurar nada manualmente
- ✅ **MySQL incluido** - Base de datos lista para usar

**Costo Real Estimado**:
- Backend Django: ~$5/mes
- Frontend Angular: ~$3/mes  
- MySQL Database: ~$5/mes
- **Total: ~$13/mes** (primer mes solo $8 con los $5 gratis)

---

## 📋 Prerequisitos

Antes de comenzar, necesitas:

1. ✅ Cuenta de GitHub (con tu código de POOGraph)
2. ✅ Correo electrónico
3. ✅ Tarjeta de crédito/débito (para verificación, no te cobrarán hasta que uses los $5 gratis)

---

## 🚀 Paso 1: Preparar tu Código para Railway

### A. Actualizar Backend para Railway

Primero vamos a preparar tu código Django para que funcione en Railway.

#### 1.1 Crear archivo `railway.json` en la raíz del proyecto

```bash
cd D:\Respaldo\Documents\UAA\POOGRAPH
```

Crea el archivo `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 1.2 Actualizar `backend_tesis/requirements.txt`

Asegúrate de que tenga estas líneas:
```txt
Django>=5.2,<6.0
djangorestframework>=3.14
django-cors-headers>=4.0
mysqlclient>=2.2
javalang>=0.13
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
gunicorn>=21.2.0
whitenoise>=6.5.0
```

#### 1.3 Crear `backend_tesis/railway.json`

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn backend_tesis.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### 1.4 Actualizar `backend_tesis/settings.py`

Agrega estas configuraciones al final del archivo:

```python
import os

# Railway Configuration
if 'RAILWAY_ENVIRONMENT' in os.environ:
    # Estamos en Railway
    DEBUG = False
    
    # Allowed hosts
    ALLOWED_HOSTS = [
        os.environ.get('RAILWAY_PUBLIC_DOMAIN', ''),
        os.environ.get('RAILWAY_STATIC_URL', ''),
        '.railway.app',
        'localhost',
        '127.0.0.1'
    ]
    
    # Database configuration for Railway MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQLDATABASE', 'railway'),
            'USER': os.environ.get('MYSQLUSER', 'root'),
            'PASSWORD': os.environ.get('MYSQLPASSWORD', ''),
            'HOST': os.environ.get('MYSQLHOST', 'localhost'),
            'PORT': os.environ.get('MYSQLPORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }
    
    # CORS Configuration
    CORS_ALLOWED_ORIGINS = [
        'https://' + os.environ.get('FRONTEND_URL', ''),
    ]
    CORS_ALLOW_CREDENTIALS = True
    
    # Static files with WhiteNoise
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Security
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Desarrollo local
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### B. Preparar Frontend para Railway

#### 1.5 Actualizar `frontend/package.json`

Agrega estos scripts:
```json
{
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build --configuration production",
    "build:railway": "npm install && ng build --configuration production",
    "watch": "ng build --watch --configuration development",
    "test": "ng test"
  }
}
```

#### 1.6 Crear `frontend/railway.json`

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run build:railway"
  }
}
```

#### 1.7 Crear `frontend/nginx.conf` (si no existe)

```nginx
server {
    listen 8080;
    server_name _;
    
    root /app/dist/tesis;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass $BACKEND_URL;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 1.8 Actualizar `frontend/src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://poograph-backend.up.railway.app' // Lo actualizaremos después
};
```

---

## 🚀 Paso 2: Subir Código a GitHub

Si aún no tienes tu código en GitHub:

```bash
cd D:\Respaldo\Documents\UAA\POOGRAPH

# Inicializar Git (si no está inicializado)
git init

# Crear .gitignore
echo "node_modules/" >> .gitignore
echo "dist/" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "codigos_fuente/*" >> .gitignore
echo "!codigos_fuente/.gitkeep" >> .gitignore

# Agregar archivos
git add .
git commit -m "Preparar para deployment en Railway"

# Crear repositorio en GitHub y subir
# (Ve a github.com y crea un nuevo repositorio llamado "POOGRAPH")
git remote add origin https://github.com/TU_USUARIO/POOGRAPH.git
git branch -M main
git push -u origin main
```

---

## 🚂 Paso 3: Crear Cuenta en Railway

### 3.1 Registrarse

1. Ve a: https://railway.app/
2. Haz clic en **"Start a New Project"** o **"Login"**
3. Selecciona **"Login with GitHub"**
4. Autoriza Railway para acceder a tu cuenta de GitHub
5. ¡Listo! Ya tienes cuenta

### 3.2 Verificar Cuenta

1. Railway te dará **$5 de crédito gratis** para empezar
2. Para obtener más crédito y evitar que se duerma, agrega una tarjeta:
   - Ve a **Settings** → **Billing**
   - Clic en **"Add Payment Method"**
   - Agrega tu tarjeta (no te cobrarán hasta que uses los $5 gratis)

---

## 🗄️ Paso 4: Crear Base de Datos MySQL

### 4.1 Crear Proyecto Nuevo

1. En Railway Dashboard, clic en **"New Project"**
2. Clic en **"Provision MySQL"**
3. Railway creará automáticamente una base de datos MySQL

### 4.2 Configurar Base de Datos

1. Haz clic en el servicio **MySQL** que se creó
2. Ve a la pestaña **"Variables"**
3. Verás estas variables (Railway las crea automáticamente):
   ```
   MYSQLHOST
   MYSQLPORT
   MYSQLUSER
   MYSQLPASSWORD
   MYSQLDATABASE
   MYSQL_URL
   ```
4. **¡No necesitas hacer nada más!** Railway ya configuró todo

### 4.3 Conectar a la Base de Datos (Opcional - para verificar)

Si quieres conectarte desde tu computadora local:

1. En el servicio MySQL, ve a **"Connect"**
2. Copia la **"MySQL Connection URL"**
3. Usa un cliente como **MySQL Workbench** o **DBeaver**

```bash
# O desde línea de comandos:
mysql -h [MYSQLHOST] -P [MYSQLPORT] -u [MYSQLUSER] -p
# Cuando te pida la contraseña, pega MYSQLPASSWORD
```

---

## 🐍 Paso 5: Deploy del Backend (Django)

### 5.1 Crear Servicio para Backend

1. En tu proyecto de Railway, clic en **"New"**
2. Selecciona **"GitHub Repo"**
3. Busca y selecciona tu repositorio **"POOGRAPH"**
4. Railway detectará automáticamente que es un proyecto con Django

### 5.2 Configurar Root Directory

1. Haz clic en el servicio que se creó
2. Ve a **"Settings"**
3. En **"Root Directory"**, escribe: `backend_tesis`
4. En **"Start Command"**, escribe:
   ```bash
   python manage.py migrate && python manage.py collectstatic --noinput && gunicorn backend_tesis.wsgi:application --bind 0.0.0.0:$PORT
   ```

### 5.3 Configurar Variables de Entorno

1. Ve a la pestaña **"Variables"**
2. Haz clic en **"New Variable"** y agrega estas:

```
RAILWAY_ENVIRONMENT=production
DJANGO_SECRET_KEY=tu-secret-key-super-larga-y-segura-cambiar-esto-123456789
PYTHONUNBUFFERED=1
```

3. Ahora **conecta el MySQL**:
   - Haz clic en **"New Variable"** → **"Add Reference"**
   - Selecciona el servicio **MySQL**
   - Agrega estas referencias una por una:
     - `MYSQLHOST` → `${{MySQL.MYSQLHOST}}`
     - `MYSQLPORT` → `${{MySQL.MYSQLPORT}}`
     - `MYSQLUSER` → `${{MySQL.MYSQLUSER}}`
     - `MYSQLPASSWORD` → `${{MySQL.MYSQLPASSWORD}}`
     - `MYSQLDATABASE` → `${{MySQL.MYSQLDATABASE}}`

### 5.4 Generar Dominio Público

1. Ve a **"Settings"**
2. En la sección **"Networking"**
3. Haz clic en **"Generate Domain"**
4. Railway te dará una URL como: `poograph-backend.up.railway.app`
5. **¡Guarda esta URL!** La necesitarás para el frontend

### 5.5 Verificar Deployment

1. Ve a la pestaña **"Deployments"**
2. Espera a que el status sea **"Success"** (toma 2-5 minutos)
3. Revisa los logs en la pestaña **"Logs"** si hay errores
4. Prueba tu backend abriendo: `https://poograph-backend.up.railway.app/`

---

## 🎨 Paso 6: Deploy del Frontend (Angular)

### 6.1 Actualizar URL del Backend

Antes de hacer deploy del frontend, actualiza la URL del backend:

1. En tu proyecto local, edita:
   `frontend/src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://poograph-backend.up.railway.app' // Tu URL de Railway
};
```

2. Haz commit y push:
```bash
git add .
git commit -m "Update backend URL for Railway"
git push
```

### 6.2 Crear Servicio para Frontend

1. En tu proyecto de Railway, clic en **"New"**
2. Selecciona **"GitHub Repo"**
3. Selecciona el **mismo repositorio** "POOGRAPH"
4. Railway creará otro servicio

### 6.3 Configurar Root Directory y Build

1. Haz clic en el nuevo servicio (Frontend)
2. Ve a **"Settings"**
3. Configura:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build --prod`
   - **Start Command**: `npx http-server dist/tesis -p $PORT`

### 6.4 Instalar http-server

Agrega `http-server` al `package.json`:

En tu proyecto local:
```bash
cd frontend
npm install --save http-server
```

Actualiza `frontend/package.json`:
```json
{
  "scripts": {
    "start:prod": "npx http-server dist/tesis -p 8080"
  },
  "dependencies": {
    // ... tus dependencias existentes
    "http-server": "^14.1.1"
  }
}
```

Commit y push:
```bash
git add .
git commit -m "Add http-server for Railway"
git push
```

### 6.5 Generar Dominio para Frontend

1. En el servicio Frontend, ve a **"Settings"** → **"Networking"**
2. Clic en **"Generate Domain"**
3. Obtendrás: `poograph-frontend.up.railway.app`

### 6.6 Actualizar CORS en Backend

Ahora necesitas actualizar las URLs permitidas en el backend:

1. En Railway, ve al servicio **Backend**
2. Ve a **"Variables"**
3. Agrega una nueva variable:
   ```
   FRONTEND_URL=poograph-frontend.up.railway.app
   ```

O edita `backend_tesis/settings.py` localmente y haz push:

```python
CORS_ALLOWED_ORIGINS = [
    'https://poograph-frontend.up.railway.app',
    'http://localhost:4200',  # Para desarrollo local
]
```

---

## ✅ Paso 7: Verificar que Todo Funcione

### 7.1 Probar Backend

Abre en tu navegador:
```
https://poograph-backend.up.railway.app/
```

Deberías ver algo (página de bienvenida o lista de endpoints).

Prueba un endpoint específico:
```
https://poograph-backend.up.railway.app/usuario
```

### 7.2 Probar Frontend

Abre:
```
https://poograph-frontend.up.railway.app/
```

Deberías ver la página de login de POOGraph.

### 7.3 Probar Conexión Completa

1. En el frontend, intenta **registrarte**
2. Luego **inicia sesión**
3. **Crea un proyecto**
4. **Escribe código** y **compila**

Si todo funciona, ¡felicidades! 🎉

---

## 🔧 Paso 8: Configuraciones Adicionales

### 8.1 Archivos Persistentes (Código de Estudiantes)

Railway usa almacenamiento efímero por defecto. Para que los archivos de código de los estudiantes persistan:

1. Ve al servicio **Backend**
2. Ve a **"Volumes"**
3. Clic en **"New Volume"**
4. Configura:
   - **Mount Path**: `/app/codigos_fuente`
5. Railway creará un volumen persistente

### 8.2 Variables de Entorno Adicionales

Agrega estas variables en el servicio Backend:

```
PORT=8000
PYTHONUNBUFFERED=1
DJANGO_SETTINGS_MODULE=backend_tesis.settings
```

### 8.3 Configurar Compiladores (Java/C++)

Railway no incluye Java/G++ por defecto. Necesitas agregarlos:

Crea `backend_tesis/nixpacks.toml`:

```toml
[phases.setup]
nixPkgs = ["python39", "gcc", "jdk17"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["python manage.py collectstatic --noinput"]

[start]
cmd = "python manage.py migrate && gunicorn backend_tesis.wsgi:application --bind 0.0.0.0:$PORT"
```

Commit y push:
```bash
git add .
git commit -m "Add nixpacks config for Java/C++"
git push
```

Railway detectará automáticamente el archivo y reinstalará con Java y G++.

---

## 💰 Paso 9: Monitorear Costos

### 9.1 Ver Uso Actual

1. En Railway, ve a **"Settings"** → **"Usage"**
2. Verás:
   - Crédito restante ($5 iniciales)
   - Uso por servicio
   - Costo proyectado del mes

### 9.2 Optimizar Costos

**Opciones para reducir costos**:

1. **Escalar servicios**:
   - Frontend no necesita mucha memoria (256MB es suficiente)
   - Backend necesita al menos 512MB (para compilación)

2. **Sleep Mode** (Solo con plan hobby):
   - Los servicios se duermen después de inactividad
   - Se despiertan automáticamente al recibir una petición
   - Primer request puede tardar 10-30 segundos

3. **Monitoreo de uso**:
   - Revisa **"Metrics"** en cada servicio
   - Ajusta recursos según necesidad real

---

## 🔍 Paso 10: Debugging y Logs

### 10.1 Ver Logs en Tiempo Real

1. Haz clic en cualquier servicio
2. Ve a la pestaña **"Logs"**
3. Verás logs en tiempo real

### 10.2 Errores Comunes y Soluciones

#### Error: "Application failed to respond"
**Solución**:
```bash
# Verifica que el Start Command sea correcto
# Backend:
python manage.py migrate && gunicorn backend_tesis.wsgi:application --bind 0.0.0.0:$PORT

# Frontend:
npx http-server dist/tesis -p $PORT
```

#### Error: "Database connection failed"
**Solución**:
1. Verifica que las variables `MYSQL*` estén conectadas
2. En Backend → Variables, asegúrate que las referencias apunten al servicio MySQL

#### Error: "CORS policy blocked"
**Solución**:
```python
# En settings.py, actualiza:
CORS_ALLOWED_ORIGINS = [
    'https://tu-frontend.up.railway.app',
]
```

#### Error: "Module not found"
**Solución**:
```bash
# Verifica que requirements.txt tenga todos los módulos
# Fuerza un rebuild:
# En Railway → Service → Settings → Redeploy
```

---

## 🎯 Checklist Final

Antes de dar acceso a los estudiantes:

- [ ] Backend desplegado y funcionando
- [ ] Frontend desplegado y accesible
- [ ] Base de datos creada y conectada
- [ ] CORS configurado correctamente
- [ ] Pueden registrarse nuevos usuarios
- [ ] Pueden crear proyectos
- [ ] Pueden escribir y compilar código
- [ ] Los archivos persisten (Volumen configurado)
- [ ] SSL/HTTPS funcionando (Railway lo hace automático)
- [ ] Costos monitoreados

---

## 📊 Resumen de URLs

Al final tendrás:

| Componente | URL | Uso |
|------------|-----|-----|
| Frontend | `https://poograph-frontend.up.railway.app` | Estudiantes acceden aquí |
| Backend API | `https://poograph-backend.up.railway.app` | API REST |
| MySQL | `[host interno].railway.app:3306` | Base de datos (solo interno) |

---

## 💡 Próximos Pasos

### Opcional: Dominio Personalizado

Si quieres usar tu propio dominio (ej: `poograph.com`):

1. Compra un dominio en Namecheap/GoDaddy (~$10/año)
2. En Railway → Service → Settings → Custom Domain
3. Agrega tu dominio
4. Railway te dará registros DNS para configurar
5. En tu proveedor de dominio, agrega los registros CNAME

### Monitoreo

1. **UptimeRobot** (gratis): https://uptimerobot.com/
   - Monitorea si tu app está online
   - Te envía alertas por email

2. **Google Analytics**: Para ver uso de estudiantes

---

## 🆘 Ayuda

Si tienes problemas:

1. Revisa los **Logs** en Railway
2. Verifica las **Variables de Entorno**
3. Asegúrate de que el **código esté en GitHub** actualizado
4. Railway tiene **documentación**: https://docs.railway.app/

---

## 🎉 ¡Listo!

Tu aplicación POOGraph ya está en internet y lista para que los estudiantes comiencen a usarla.

**URLs finales** (ejemplos, las tuyas serán diferentes):
- 🌐 Frontend: https://poograph-frontend.up.railway.app
- ⚙️ Backend: https://poograph-backend.up.railway.app

**Costo mensual estimado**: ~$13/mes (primer mes ~$8 con los $5 gratis)

---

**¿Tienes algún error o duda específica en algún paso?** Puedo ayudarte a resolverlo. 🚀

