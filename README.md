# 🎓 POOGraph - Plataforma Educativa para Programación Orientada a Objetos

![POOGraph](https://img.shields.io/badge/Version-1.0-blue)
![Angular](https://img.shields.io/badge/Angular-13.3-red)
![Django](https://img.shields.io/badge/Django-5.2-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)

**POOGraph** es una aplicación web educativa desarrollada como proyecto de tesis para la enseñanza y análisis del aprendizaje de Programación Orientada a Objetos (POO). La plataforma permite a los estudiantes escribir código Java o C++, visualizar sus clases en diagramas UML en tiempo real, compilar y ejecutar sus programas, todo mientras se recolectan datos de interacción para análisis predictivo del rendimiento estudiantil.

---

## 🎯 Características Principales

✨ **Editor de Código Profesional** (Monaco Editor)
- Syntax highlighting para Java y C++
- Autocompletado inteligente
- Tema personalizado "POOGraph Dark"
- Tooltips educativos interactivos

📊 **Visualización UML en Tiempo Real**
- Diagrama de clases automático
- Flechas de herencia dinámicas
- Actualización en vivo al modificar código

▶️ **Compilación y Ejecución Integrada**
- Compila proyectos completos (Java/C++)
- Terminal integrada con output
- Manejo de errores de compilación
- Soporte para entrada de usuario

🧠 **Learning Analytics**
- Registro de tooltips consultados
- Logs de actividad del estudiante
- Detección de intentos de plagio
- Análisis predictivo con Machine Learning

✅ **Sistema de Exámenes**
- Creación de exámenes de opción múltiple
- Temporizador automático
- Calificación instantánea
- Historial de intentos

📈 **Dashboard para Profesores**
- Métricas de uso de la plataforma
- Análisis de conceptos difíciles
- Gráficas de rendimiento
- Exportación de datos

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│  Frontend (Angular 13)                              │
│  - Monaco Editor                                    │
│  - ngx-graph (Diagramas UML)                       │
│  - Angular Material                                 │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────────┐
│  Backend (Django 5.2)                               │
│  - Django REST Framework                            │
│  - javalang (Parser AST)                           │
│  - pandas/scikit-learn (Analytics)                 │
└─────────────────┬───────────────────────────────────┘
                  │ MySQL Driver
┌─────────────────▼───────────────────────────────────┐
│  Database (MySQL 8.0)                               │
│  - 15+ tablas relacionales                          │
│  - Vistas para herencia                             │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Instalación Rápida con Docker

### Prerequisitos
- Docker Desktop instalado
- Docker Compose

### Pasos

1. **Clonar el repositorio**
```bash
git clone <URL_DEL_REPOSITORIO>
cd POOGRAPH
```

2. **Levantar los servicios**
```bash
docker-compose up -d
```

3. **Acceder a la aplicación**
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- Base de Datos: localhost:3307

4. **Crear un superusuario (opcional)**
```bash
docker-compose exec backend python manage.py createsuperuser
```

5. **Acceder al admin de Django**
- URL: http://localhost:8000/admin

---

## 🛠️ Instalación Manual (Desarrollo)

### Backend (Django)

#### Prerequisitos
- Python 3.9+
- MySQL 8.0
- Java JDK 11+ (para compilación)
- g++ (para C++)

#### Pasos

1. **Navegar al directorio del backend**
```bash
cd backend_tesis
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements-docker.txt
```

5. **Configurar base de datos**

Crear la base de datos MySQL:
```sql
CREATE DATABASE clases CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON clases.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

Editar `backend_tesis/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clases',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

6. **Ejecutar migraciones** (si managed=True)
```bash
python manage.py migrate
```

7. **Crear superusuario**
```bash
python manage.py createsuperuser
```

8. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

Backend corriendo en: http://localhost:8000

---

### Frontend (Angular)

#### Prerequisitos
- Node.js 14+ y npm
- Angular CLI 13+

#### Pasos

1. **Navegar al directorio del frontend**
```bash
cd frontend
```

2. **Instalar Angular CLI** (si no está instalado)
```bash
npm install -g @angular/cli@13
```

3. **Instalar dependencias**
```bash
npm install
```

4. **Configurar URL del backend**

Editar `src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

5. **Ejecutar servidor de desarrollo**
```bash
ng serve
```

Frontend corriendo en: http://localhost:4200

---

## 📁 Estructura del Proyecto

```
POOGRAPH/
│
├── backend_tesis/              # Backend Django
│   ├── backend_tesis/          # Configuración
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/                   # App principal
│   │   ├── models.py           # 15+ modelos
│   │   ├── views.py            # 30+ endpoints
│   │   └── admin.py
│   ├── codigos_fuente/         # Código de estudiantes
│   ├── archivos/               # Imágenes UML
│   ├── datos/                  # CSVs de logs
│   ├── manage.py
│   ├── requirements-docker.txt
│   └── Dockerfile
│
├── frontend/                   # Frontend Angular
│   ├── src/app/
│   │   ├── login/              # Autenticación
│   │   ├── register/           # Registro
│   │   ├── home/               # Lista proyectos
│   │   ├── area-de-trabajo/    # Editor principal
│   │   ├── dashboard/          # Analytics
│   │   ├── hacer-examen/       # Sistema exámenes
│   │   ├── dialogs/            # Modales
│   │   ├── services/           # Servicios API
│   │   └── guards/             # Protección rutas
│   ├── package.json
│   ├── angular.json
│   ├── nginx.conf
│   └── Dockerfile
│
├── docker-compose.yml          # Orquestación
├── ejercicios/                 # Material didáctico
└── README.md
```

---

## 🔌 API Endpoints Principales

### Autenticación
```
POST   /api/login/              # Iniciar sesión
POST   /api/logout/             # Cerrar sesión
POST   /api/register/           # Registrar usuario
```

### Proyectos
```
POST   /proyecto                # Crear proyecto
GET    /proyecto/<id>           # Proyectos de usuario
POST   /proyectoIndividual      # Detalle de proyecto
```

### Clases
```
GET    /clasesProyectId/<id>    # Listar clases
POST   /clases                  # Crear clase
DELETE /clase/<id>              # Eliminar clase
GET    /clase-info/<id>         # Info completa
```

### Código
```
GET    /clases/<id>/codigo      # Obtener código
POST   /guardar-archivo         # Guardar cambios
POST   /compilar-proyecto       # Compilar/ejecutar
GET    /archivos-proyecto/<id>  # Listar archivos
```

### Exámenes
```
POST   /examenes/crear          # Crear examen
GET    /examenes/disponibles/<id> # Listar disponibles
POST   /examenes/iniciar        # Iniciar intento
POST   /examenes/enviar         # Enviar respuestas
GET    /examenes/resultados/<id> # Ver resultados
```

### Analytics
```
POST   /api/tooltip-log         # Registrar tooltip
GET    /api/dashboard-analytics # Métricas del dashboard
```

**Documentación completa**: Ver `DOCUMENTACION_TECNICA_POOGRAPH.md`

---

## 🗄️ Modelo de Base de Datos

### Tablas Principales

- **usuario**: Información de estudiantes/profesores (con datos demográficos)
- **proyecto**: Proyectos de programación (Java/C++)
- **clase**: Clases dentro de proyectos
- **atributos**: Atributos de clases
- **funciones**: Métodos de clases
- **herencia**: Relaciones de herencia
- **log_actividad**: Logs de interacción
- **examen**, **pregunta**, **opcion**: Sistema de evaluación
- **intento_examen**, **respuesta_estudiante**: Historial de exámenes

### Vistas
- **herenciaf**: Herencia con nombres de clases
- **getatributos**: Atributos con contexto
- **getfunciones**: Funciones con contexto

**Diagrama ER completo**: Ver `DOCUMENTACION_TECNICA_POOGRAPH.md`

---

## 🎓 Uso de la Plataforma

### Para Estudiantes

1. **Registrarse** con datos demográficos
2. **Crear un proyecto** (Java o C++)
3. **Escribir código** en el editor Monaco
4. **Ver diagrama UML** actualizado en tiempo real
5. **Compilar y ejecutar** con el botón "▶️"
6. **Usar tooltips** haciendo doble clic en keywords
7. **Realizar exámenes** asignados por el profesor

### Para Profesores

1. **Acceder al Dashboard** para ver métricas
2. **Crear exámenes** con preguntas de opción múltiple
3. **Ver analytics** de conceptos difíciles
4. **Exportar datos** para análisis externo
5. **Monitorear progreso** de estudiantes

**Manual completo**: Ver `MANUAL_USUARIO_POOGRAPH.md`

---

## 🧪 Testing

### Backend
```bash
cd backend_tesis
python manage.py test
```

### Frontend
```bash
cd frontend
ng test
```

### E2E (Karma)
```bash
cd frontend
ng e2e
```

---

## 📊 Learning Analytics

POOGraph recolecta datos de interacción para investigación educativa:

### Datos Demográficos
- Género, edad, nivel socioeconómico, semestre

### Eventos Registrados
- **Tooltips consultados**: Qué conceptos necesitan ayuda
- **Intentos de pegado**: Detección de plagio
- **Compilaciones**: Frecuencia, éxito/fracaso
- **Toggle de diagrama**: Uso de visualización
- **Tiempo de sesión**: Duración de trabajo

### Análisis con Machine Learning
- Predicción de rendimiento (scikit-learn)
- Comparación: POOGraph vs enseñanza tradicional
- Identificación de patrones de dificultad

**Nota**: Los datos son anónimos y solo para fines de investigación académica.

---

## 🔐 Seguridad

### Frontend
- Almacenamiento encriptado con AES-256 (Crypto-JS)
- Guards de Angular para rutas protegidas
- Validación de formularios

### Backend
- Django sessions con cookies seguras
- CSRF protection habilitada
- Password hashing con PBKDF2 SHA-256
- SQL injection prevention con ORM
- CORS configurado restrictivamente

### Buenas Prácticas
- Nunca commitear credenciales
- Usar variables de entorno para secrets
- HTTPS en producción

---

## 🐛 Solución de Problemas

### Error: "No se puede conectar al backend"
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/

# Revisar CORS en settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]
```

### Error: "Compilador no encontrado"
```bash
# Instalar Java JDK
# Windows: https://adoptium.net/
# Linux: sudo apt install default-jdk

# Instalar g++ (C++)
# Windows: MinGW
# Linux: sudo apt install g++

# Verificar instalación
java -version
javac -version
g++ --version
```

### Error: "MySQL connection refused"
```bash
# Iniciar MySQL
# Windows: Services > MySQL > Start
# Linux: sudo systemctl start mysql

# Verificar puerto
netstat -an | grep 3306
```

### Frontend no carga después de npm install
```bash
# Limpiar cache
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Reinstalar Angular CLI
npm install -g @angular/cli@13
```

---

## 📝 Contribución

Este proyecto es parte de una investigación de tesis. Para contribuir:

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es parte de una investigación académica de la Universidad Autónoma de Aguascalientes.

**Uso educativo únicamente**.

---

## 👥 Autores

**Proyecto de Tesis**  
Ingeniería en Sistemas Computacionales  
Universidad Autónoma de Aguascalientes  
2026

---

## 📞 Soporte

Para preguntas o problemas técnicos:
- **Issues**: Abre un issue en GitHub
- **Email**: [Contacto del profesor/estudiante]

---

## 📚 Documentación Adicional

- **Documentación Técnica Completa**: `DOCUMENTACION_TECNICA_POOGRAPH.md`
- **Manual de Usuario**: `MANUAL_USUARIO_POOGRAPH.md`
- **Diagrama de Módulos**: `DIAGRAMA_MODULOS_POOGRAPH.md`

---

## 🚀 Roadmap

### Versión 1.0 (Actual)
- ✅ Editor Monaco con Java y C++
- ✅ Diagrama UML en tiempo real
- ✅ Compilación y ejecución
- ✅ Sistema de exámenes
- ✅ Dashboard de analytics
- ✅ Tooltips educativos

### Versión 1.1 (Planeada)
- [ ] Soporte para interfaces en UML
- [ ] Autoguardado con indicador visual
- [ ] Tests unitarios automatizados
- [ ] Modo oscuro/claro para diagrama

### Versión 2.0 (Futuro)
- [ ] Colaboración en tiempo real (WebSockets)
- [ ] Integración con GitHub
- [ ] Modelo ML para predicción de rendimiento
- [ ] Sugerencias de código con IA
- [ ] Soporte para Python y C#
- [ ] PWA con modo offline

---

## 🌟 Características Educativas Especiales

### 1. Tooltips Contextuales
- Doble clic en keywords muestra explicaciones
- Diferenciado por lenguaje (Java vs C++)
- Registro automático para analytics

### 2. Anti-Plagio
- Pegado de código bloqueado
- Detección y registro de intentos

### 3. Visualización Activa
- Diagrama se actualiza al guardar
- Relaciones de herencia automáticas
- Interacción con nodos para ver detalles

### 4. Feedback Inmediato
- Errores de compilación en terminal
- Ejecución directa con output
- Calificación instantánea en exámenes

---

**¡Aprende POO de forma visual e interactiva con POOGraph! 🎓✨**

