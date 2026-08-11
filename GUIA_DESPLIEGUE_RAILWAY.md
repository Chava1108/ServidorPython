# 🚀 Guía Completa de Despliegue en Railway - Proyecto de Tesis

Esta guía te llevará paso a paso para desplegar tu aplicación completa (Backend Django + Frontend Angular + Base de Datos MySQL) en Railway.

---

## 📋 Índice
1. [Preparación Inicial](#1-preparación-inicial)
2. [Crear Cuenta en Railway](#2-crear-cuenta-en-railway)
3. [Subir Código a GitHub](#3-subir-código-a-github)
4. [Desplegar la Base de Datos MySQL](#4-desplegar-la-base-de-datos-mysql)
5. [Desplegar el Backend (Django)](#5-desplegar-el-backend-django)
6. [Desplegar el Frontend (Angular)](#6-desplegar-el-frontend-angular)
7. [Conectar Todo](#7-conectar-todo)
8. [Verificación Final](#8-verificación-final)
9. [Solución de Problemas Comunes](#9-solución-de-problemas-comunes)

---

## 1. Preparación Inicial

### 1.1 Requisitos Previos
- ✅ Cuenta de GitHub (si no tienes, créala en https://github.com)
- ✅ Git instalado en tu computadora
- ✅ Tu código funcionando localmente

### 1.2 Estructura de tu Proyecto
Tu proyecto tiene 3 componentes que se desplegarán por separado:

```
POOGRAPH/
├── backend_tesis/     → Se desplegará como servicio Django
├── frontend/          → Se desplegará como sitio estático Angular
└── (MySQL)            → Se creará como servicio en Railway
```

---

## 2. Crear Cuenta en Railway

### Paso 2.1: Registro
1. Ve a **https://railway.app**
2. Haz clic en **"Login"** (esquina superior derecha)
3. Selecciona **"Login with GitHub"** (recomendado)
4. Autoriza Railway para acceder a tu GitHub
5. Completa el registro si te lo pide

### Paso 2.2: Plan Gratuito
- Railway ofrece **$5 USD gratis** cada mes
- Para tu tesis esto debería ser suficiente para pruebas
- Si necesitas más, puedes agregar método de pago después

---

## 3. Subir Código a GitHub

### Paso 3.1: Crear Repositorio para el Backend

1. Ve a **https://github.com/new**
2. Nombre del repositorio: `tesis-backend` (o el que prefieras)
3. Marca como **Private** (privado) - es tu tesis
4. **NO** marques "Add README" (ya tienes código)
5. Clic en **"Create repository"**

### Paso 3.2: Subir Backend a GitHub

Abre una terminal/CMD en la carpeta `backend_tesis` y ejecuta:

```bash
# Navega a la carpeta del backend
cd D:\Respaldo\Documents\UAA\POOGRAPH\backend_tesis

# Inicializa git (si no está inicializado)
git init

# Agrega todos los archivos
git add .

# Crea el primer commit
git commit -m "Primer commit - Backend Django"

# Conecta con tu repositorio de GitHub (cambia TU_USUARIO por tu usuario)
git remote add origin https://github.com/TU_USUARIO/tesis-backend.git

# Sube el código
git branch -M main
git push -u origin main
```

### Paso 3.3: Crear Repositorio para el Frontend

1. Ve a **https://github.com/new**
2. Nombre: `tesis-frontend`
3. Marca como **Private**
4. Clic en **"Create repository"**

### Paso 3.4: Subir Frontend a GitHub

```bash
# Navega a la carpeta del frontend
cd D:\Respaldo\Documents\UAA\POOGRAPH\frontend

# Inicializa git (si no está inicializado)
git init

# Agrega todos los archivos
git add .

# Crea el primer commit
git commit -m "Primer commit - Frontend Angular"

# Conecta con tu repositorio de GitHub
git remote add origin https://github.com/TU_USUARIO/tesis-frontend.git

# Sube el código
git branch -M main
git push -u origin main
```

---

## 4. Desplegar la Base de Datos MySQL

### Paso 4.1: Crear Nuevo Proyecto en Railway

1. Ve a **https://railway.app/dashboard**
2. Clic en **"New Project"** (botón morado)
3. Selecciona **"Empty Project"**
4. Se creará un proyecto vacío

### Paso 4.2: Agregar MySQL

1. Dentro de tu proyecto, clic en **"+ New"** (arriba a la derecha)
2. Selecciona **"Database"**
3. Selecciona **"Add MySQL"**
4. Espera ~30 segundos mientras se crea

### Paso 4.3: Obtener Credenciales de MySQL

1. Haz clic en el servicio **MySQL** que acabas de crear
2. Ve a la pestaña **"Variables"**
3. Verás variables como:
   - `MYSQL_HOST` → El host de tu base de datos
   - `MYSQL_PORT` → Puerto (generalmente 3306)
   - `MYSQL_USER` → Usuario
   - `MYSQL_PASSWORD` → Contraseña
   - `MYSQL_DATABASE` → Nombre de la base de datos
   - `MYSQL_URL` → URL completa de conexión

**⚠️ IMPORTANTE:** Guarda estos valores, los necesitarás para el backend.

### Paso 4.4: Crear la Base de Datos

1. En el servicio MySQL, ve a la pestaña **"Data"**
2. Esto abre una consola MySQL
3. Ejecuta:
```sql
CREATE DATABASE IF NOT EXISTS clases CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 5. Desplegar el Backend (Django)

### Paso 5.1: Agregar el Servicio Backend

1. En tu proyecto de Railway, clic en **"+ New"**
2. Selecciona **"GitHub Repo"**
3. Si es la primera vez, autoriza Railway para acceder a tus repos
4. Busca y selecciona **"tesis-backend"**
5. Railway detectará automáticamente que es Python

### Paso 5.2: Configurar Variables de Entorno

1. Haz clic en el servicio del backend
2. Ve a la pestaña **"Variables"**
3. Clic en **"+ New Variable"** y agrega CADA una de estas:

| Variable | Valor |
|----------|-------|
| `SECRET_KEY` | `tu-clave-secreta-muy-larga-y-segura-12345` |
| `DEBUG` | `False` |
| `DB_NAME` | (copia el valor de `MYSQL_DATABASE` del servicio MySQL) |
| `DB_USER` | (copia el valor de `MYSQL_USER` del servicio MySQL) |
| `DB_PASSWORD` | (copia el valor de `MYSQL_PASSWORD` del servicio MySQL) |
| `DB_HOST` | (copia el valor de `MYSQL_HOST` del servicio MySQL) |
| `DB_PORT` | (copia el valor de `MYSQL_PORT` del servicio MySQL) |

**💡 TIP:** Puedes usar "Reference" para conectar variables automáticamente:
1. En vez de copiar/pegar, clic en **"+ New Variable"**
2. Clic en **"Add Reference"**
3. Selecciona el servicio MySQL
4. Selecciona la variable correspondiente

### Paso 5.3: Verificar archivos de configuración

Asegúrate de que tu repositorio tenga estos archivos (ya los creamos):

**`requirements.txt`** o **`requirements-railway.txt`** con:
```
Django>=5.2,<6.0
djangorestframework>=3.14
django-cors-headers>=4.0
mysqlclient>=2.2
gunicorn>=21.0
whitenoise>=6.6
javalang>=0.13
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
```

**`Procfile`** con:
```
web: gunicorn backend_tesis.wsgi --bind 0.0.0.0:$PORT
```

### Paso 5.4: Configurar el Build

1. En tu servicio backend, ve a **"Settings"**
2. En la sección **"Build"**:
   - Build Command: `pip install -r requirements-railway.txt`
3. En la sección **"Deploy"**:
   - Start Command: `python manage.py collectstatic --noinput && python manage.py migrate && gunicorn backend_tesis.wsgi`

### Paso 5.5: Generar Dominio Público

1. En **"Settings"** del backend
2. Busca la sección **"Networking"**
3. Clic en **"Generate Domain"**
4. Se generará algo como: `tesis-backend-production.up.railway.app`
5. **¡COPIA ESTA URL!** La necesitarás para el frontend

### Paso 5.6: Desplegar

1. Clic en **"Deploy"** o espera a que inicie automáticamente
2. Ve a la pestaña **"Deployments"** para ver el progreso
3. Clic en el deployment para ver los logs
4. Espera a que diga "Deployment successful"

### Paso 5.7: Verificar Backend

1. Abre en tu navegador: `https://TU-BACKEND.railway.app/admin/`
2. Deberías ver la página de login de Django Admin
3. Si ves errores, revisa los logs en la pestaña "Deployments"

---

## 6. Desplegar el Frontend (Angular)

### Paso 6.1: Actualizar URL del Backend

**IMPORTANTE:** Antes de desplegar, actualiza el archivo `environment.prod.ts`:

```typescript
// frontend/src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://TU-BACKEND-URL.railway.app/'  // ← Pon tu URL real aquí
};
```

Haz commit y push de este cambio:
```bash
cd D:\Respaldo\Documents\UAA\POOGRAPH\frontend
git add .
git commit -m "Actualizar URL del backend para producción"
git push
```

### Paso 6.2: Agregar el Servicio Frontend

1. En tu proyecto de Railway, clic en **"+ New"**
2. Selecciona **"GitHub Repo"**
3. Busca y selecciona **"tesis-frontend"**

### Paso 6.3: Configurar el Build para Angular

1. Clic en el servicio frontend
2. Ve a **"Settings"**
3. En **"Build"**:
   - **Build Command:** `npm install && npm run build -- --configuration production`
4. En **"Deploy"**:
   - Para servir archivos estáticos, necesitas un servidor. Railway usará Node por defecto.

### Paso 6.4: Crear archivo para servir Angular

Necesitas agregar un servidor simple para servir los archivos. Crea este archivo en tu frontend:

**`server.js`** (en la raíz del frontend):
```javascript
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4200;

// Servir archivos estáticos desde dist/tesis
app.use(express.static(path.join(__dirname, 'dist/tesis')));

// Para Angular routing - redirigir todas las rutas a index.html
app.get('/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist/tesis/index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});
```

Y agrega express a tu package.json (en devDependencies o dependencies):
```bash
npm install express --save
```

### Paso 6.5: Actualizar package.json

Agrega un script de start:
```json
{
  "scripts": {
    "start": "node server.js",
    "build": "ng build",
    ...
  }
}
```

### Paso 6.6: Configurar Railway para Frontend

1. En **"Settings"** del servicio frontend:
   - **Build Command:** `npm install && npm run build -- --configuration production`
   - **Start Command:** `npm start`

### Paso 6.7: Generar Dominio para Frontend

1. En **"Settings"** → **"Networking"**
2. Clic en **"Generate Domain"**
3. Obtendrás algo como: `tesis-frontend-production.up.railway.app`

---

## 7. Conectar Todo

### Paso 7.1: Actualizar CORS en Backend

Agrega la URL de tu frontend a las variables del backend:

1. Ve al servicio Backend en Railway
2. Ve a **"Variables"**
3. Agrega:
   - `FRONTEND_URL` = `https://tesis-frontend-production.up.railway.app`

### Paso 7.2: Re-desplegar Backend

1. En el servicio backend
2. Ve a **"Deployments"**
3. Clic en los 3 puntos del último deployment
4. Selecciona **"Redeploy"**

### Paso 7.3: Crear Superusuario (Admin)

Para crear un usuario administrador:

1. En el servicio backend, ve a **"Settings"**
2. Busca **"Railway Shell"** o ve a la pestaña **"Shell"**
3. Ejecuta:
```bash
python manage.py createsuperuser
```
4. Sigue las instrucciones (email, contraseña)

---

## 8. Verificación Final

### Checklist de Verificación

| Servicio | URL | Qué verificar |
|----------|-----|---------------|
| MySQL | (interno) | Conectarse desde backend |
| Backend | `https://tu-backend.railway.app/admin/` | Ver página de admin |
| Backend API | `https://tu-backend.railway.app/api/` | Ver respuesta JSON |
| Frontend | `https://tu-frontend.railway.app/` | Ver tu aplicación |

### Probar el Flujo Completo

1. Abre tu frontend: `https://tu-frontend.railway.app/`
2. Intenta hacer login (si tienes esa funcionalidad)
3. Verifica que los datos se carguen correctamente
4. Revisa la consola del navegador (F12) por errores de CORS

---

## 9. Solución de Problemas Comunes

### Error: "Application failed to respond"
**Causa:** El servidor no está escuchando en el puerto correcto.
**Solución:** Asegúrate de usar `$PORT` o `process.env.PORT` en tu código.

### Error: "CORS policy"
**Causa:** El frontend no está en la lista de orígenes permitidos.
**Solución:**
1. Ve a Variables del backend
2. Verifica que `FRONTEND_URL` tenga la URL correcta de tu frontend
3. Re-despliega el backend

### Error: "Database connection failed"
**Causa:** Credenciales incorrectas de MySQL.
**Solución:**
1. Verifica que todas las variables DB_* estén configuradas
2. Usa "Reference" para conectar las variables automáticamente
3. Verifica que la base de datos exista

### Error: "Module not found"
**Causa:** Falta alguna dependencia en requirements.txt.
**Solución:** Agrega la dependencia faltante y haz push.

### El frontend se ve en blanco
**Causa:** Los archivos no se están sirviendo correctamente.
**Solución:**
1. Verifica que el build se completó (revisa logs)
2. Verifica que server.js apunta a la carpeta correcta (`dist/tesis`)

### Error: "collectstatic failed"
**Causa:** Problema con archivos estáticos.
**Solución:** Asegúrate de que whitenoise esté instalado y configurado.

---

## 📝 Resumen de URLs Importantes

Después de completar el despliegue, tendrás:

| Servicio | URL |
|----------|-----|
| Frontend | `https://[tu-proyecto]-frontend.up.railway.app` |
| Backend | `https://[tu-proyecto]-backend.up.railway.app` |
| Admin Django | `https://[tu-proyecto]-backend.up.railway.app/admin/` |
| API | `https://[tu-proyecto]-backend.up.railway.app/api/` |

---

## 💰 Costos Estimados

- **Plan gratuito:** $5 USD/mes incluidos
- **Tu proyecto aproximado:**
  - MySQL: ~$2-3/mes
  - Backend: ~$1-2/mes
  - Frontend: ~$0.50-1/mes
  - **Total: ~$3-5/mes** (dentro del crédito gratuito)

---

## 🆘 Soporte

Si tienes problemas:
1. Revisa los **logs** de cada servicio en Railway
2. Consulta la documentación: https://docs.railway.app
3. Únete al Discord de Railway para ayuda de la comunidad

---

**¡Éxito con tu tesis! 🎓**
