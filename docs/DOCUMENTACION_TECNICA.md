# 📚 Documentación Técnica - POOGraph

## 🎯 Descripción General del Proyecto

**POOGraph** es una aplicación web educativa desarrollada como proyecto de tesis para la recolección y análisis de datos de estudiantes que están aprendiendo Programación Orientada a Objetos (POO). 

El sistema permite:
- Crear y gestionar proyectos de programación (Java y C++)
- Visualizar diagramas UML en tiempo real
- Escribir código con un editor integrado (Monaco Editor)
- Compilar y ejecutar código
- Realizar exámenes evaluativos
- Recolectar logs de actividad para análisis predictivo del rendimiento estudiantil
- Comparar la efectividad del aprendizaje con herramientas digitales vs enseñanza tradicional

---

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico

#### **Frontend**
- **Framework**: Angular 13.3.0
- **Lenguaje**: TypeScript 4.6.2
- **Editor de Código**: Monaco Editor 0.33.0
- **Visualización de Grafos**: @swimlane/ngx-graph 8.0.2
- **UI Components**: Angular Material 13.3.9
- **Gráficas**: Chart.js 3.9.1
- **Seguridad**: Crypto-JS 4.2.0
- **Layout**: Angular Split 13.2.0

#### **Backend**
- **Framework**: Django 5.2+
- **API**: Django REST Framework 3.14+
- **Base de Datos**: MySQL 8.0
- **CORS**: django-cors-headers 4.0+
- **Parseo de Código**: javalang 0.13+
- **Análisis de Datos**: pandas 2.0+, numpy 1.24+, scikit-learn 1.3+

#### **Infraestructura**
- **Contenedorización**: Docker + Docker Compose
- **Servidor Web**: Nginx (para frontend en producción)
- **Servidor de Aplicación**: Gunicorn/Uvicorn (Django)

---

## 📁 Estructura del Proyecto

```
POOGRAPH/
├── backend_tesis/          # Backend Django
│   ├── backend_tesis/      # Configuración principal
│   │   ├── settings.py     # Configuración del proyecto
│   │   ├── urls.py         # Rutas principales
│   │   └── wsgi.py         # WSGI application
│   ├── core/               # Aplicación principal
│   │   ├── models.py       # Modelos de BD
│   │   └── views.py        # Lógica de negocio
│   ├── codigos_fuente/     # Archivos de código de estudiantes
│   ├── datos/              # Logs y datos CSV
│   ├── archivos/           # Archivos multimedia
│   ├── manage.py           # CLI de Django
│   ├── requirements-docker.txt
│   └── Dockerfile
│
├── frontend/               # Frontend Angular
│   ├── src/
│   │   └── app/
│   │       ├── area-de-trabajo/     # Editor principal
│   │       ├── dashboard/           # Panel de administración
│   │       ├── login/               # Autenticación
│   │       ├── register/            # Registro de usuarios
│   │       ├── home/                # Vista de proyectos
│   │       ├── hacer-examen/        # Módulo de exámenes
│   │       ├── realizar-test/       # Tests evaluativos
│   │       ├── dialogs/             # Modales y diálogos
│   │       │   ├── showclass/       # Visualizar clase
│   │       │   ├── formulario/      # Crear clase
│   │       │   ├── editar-formulario/ # Editar clase
│   │       │   └── form-proyect/    # Crear proyecto
│   │       ├── services/            # Servicios de API
│   │       └── guards/              # Protección de rutas
│   ├── package.json
│   ├── angular.json
│   ├── nginx.conf
│   └── Dockerfile
│
├── docker-compose.yml      # Orquestación de servicios
├── ejercicios/             # Ejercicios de práctica
└── Laboratorio/            # Material de laboratorio
```

---

## 💾 Modelo de Base de Datos

### Entidades Principales

#### **Usuario**
```python
Usuario (AbstractBaseUser)
- id (PK, AutoIncrement)
- username (unique)
- email (unique)
- name
- password (encriptado)
- genero (M/F/O)
- edad
- nivel_socioeconomico
- semestre
- is_active
- is_admin
```

#### **Proyecto**
```python
Proyecto
- id (PK)
- nombre
- id_usr (FK → Usuario)
- lenguaje ('java' | 'cpp')
```

#### **Clase**
```python
Clase
- id (PK)
- nombre
- nivel ('public' | 'private' | 'protected')
- id_proyecto (FK → Proyecto)
- imagen (path)
- path_archivo
- UNIQUE(nombre, id_proyecto)
```

#### **Atributos**
```python
Atributos
- id (PK)
- nombre
- tipo (int, String, boolean, etc.)
- nivel ('public' | 'private' | 'protected')
- id_clase (FK → Clase)
```

#### **Funciones**
```python
Funciones
- id (PK)
- nombre
- tipo (void, int, String, etc.)
- nivel ('public' | 'private' | 'protected')
- id_clase (FK → Clase)
```

#### **Herencia**
```python
Herencia
- id (PK)
- id_clasePadre (FK → Clase)
- id_claseHijo (FK → Clase, unique)
```

#### **LogActividad**
```python
LogActividad
- id (PK)
- usuario (username)
- accion (string)
- detalle (text)
- fecha (datetime, default=now)
```

#### **Examen**
```python
Examen
- id (PK)
- titulo
- creado_por (FK → Usuario)
- fecha_disponible
- duracion_minutos
- activo (boolean)
- fecha_creacion
```

#### **Pregunta**
```python
Pregunta
- id (PK)
- examen (FK → Examen)
- texto
- orden
```

#### **Opcion**
```python
Opcion
- id (PK)
- pregunta (FK → Pregunta)
- texto
- es_correcta (boolean)
```

#### **IntentoExamen**
```python
IntentoExamen
- id (PK)
- examen (FK → Examen)
- estudiante (FK → Usuario)
- fecha_inicio
- fecha_fin
- completado (boolean)
```

#### **RespuestaEstudiante**
```python
RespuestaEstudiante
- id (PK)
- intento (FK → IntentoExamen)
- pregunta (FK → Pregunta)
- opcion_seleccionada (FK → Opcion)
```

### Vistas de Base de Datos

#### **herenciaf** (Vista)
```sql
SELECT 
    hijo.nombre AS Hijo,
    padre.nombre AS Padre,
    hijo.id_proyecto
FROM herencia h
JOIN clase hijo ON h.id_claseHijo = hijo.id
JOIN clase padre ON h.id_clasePadre = padre.id
```

#### **getatributos** (Vista)
```sql
SELECT 
    a.id,
    c.nombre,
    a.nivel,
    a.tipo,
    a.nombre AS atributos
FROM atributos a
JOIN clase c ON a.id_clase = c.id
```

#### **getfunciones** (Vista)
```sql
SELECT 
    f.id,
    c.nombre,
    f.nivel,
    f.tipo,
    f.nombre AS funciones
FROM funciones f
JOIN clase c ON f.id_clase = c.id
```

---

## 🔌 API Endpoints

### **Autenticación**
```
POST   /api/login/                  # Iniciar sesión
POST   /api/logout/                 # Cerrar sesión
POST   /api/register/               # Registrar usuario
```

### **Usuarios**
```
GET    /usuario                     # Listar usuarios
POST   /usuario                     # Crear usuario
```

### **Proyectos**
```
POST   /proyecto                    # Crear proyecto
GET    /proyecto/<id>               # Proyectos de un usuario
POST   /proyectoIndividual          # Obtener proyecto específico
```

### **Clases**
```
GET    /clasesProyectId/<id>        # Clases de un proyecto
POST   /clases                      # Crear clase
DELETE /clase/<id>                  # Eliminar clase
GET    /clase-info/<id_clase>       # Info completa (propios + heredados)
GET    /clase-info/<id_clase>/codigo-funcion  # Código de función específica
GET    /clases/<id>/codigo          # Código fuente de la clase
```

### **Atributos y Funciones**
```
POST   /atributos                   # Agregar atributo (inyecta en archivo)
POST   /funciones                   # Agregar función (inyecta en archivo)
```

### **Herencia**
```
POST   /herencia                    # Agregar extends (modifica archivo)
```

### **Gestión de Archivos**
```
POST   /upload                      # Subir archivo
GET    /archivos-proyecto/<proyecto_id>  # Listar archivos
POST   /leer-archivo                # Leer contenido de archivo
POST   /guardar-archivo             # Guardar cambios en archivo
POST   /compilar-proyecto           # Compilar y ejecutar
```

### **Analytics**
```
POST   /api/tooltip-log             # Registrar tooltip consultado
GET    /api/dashboard-analytics     # Métricas del dashboard
```

### **Exámenes**
```
POST   /examenes/crear              # Crear examen (profesor)
GET    /examenes                    # Listar todos los exámenes
GET    /examenes/disponibles/<id_estudiante>  # Exámenes disponibles
GET    /examenes/<id_examen>/estudiante       # Detalle del examen
POST   /examenes/iniciar            # Iniciar intento de examen
POST   /examenes/enviar             # Enviar respuestas
GET    /examenes/resultados/<id_intento>      # Resultados del intento
```

---

## 🎨 Módulos del Frontend

### **1. Login & Register**
- **Componentes**: `LoginComponent`, `RegisterComponent`
- **Funcionalidad**: 
  - Autenticación con JWT
  - Registro de nuevos estudiantes
  - Captura de datos demográficos (género, edad, nivel socioeconómico, semestre)
  - Almacenamiento seguro con encriptación AES

### **2. Home (Lista de Proyectos)**
- **Componente**: `HomeComponent`
- **Funcionalidad**:
  - Ver proyectos del usuario
  - Crear nuevo proyecto (Java o C++)
  - Seleccionar proyecto para trabajar
  - Eliminar proyectos

### **3. Área de Trabajo (Editor Principal)**
- **Componente**: `AreaDeTrabajoComponent`
- **Características**:
  - **Editor Monaco** con syntax highlighting
  - **Tema personalizado** (POOGraph Dark)
  - **Tooltips educativos** por doble clic
  - **Bloqueo de pegado** (anti-plagio)
  - **Explorador de archivos** del proyecto
  - **Diagrama UML** en tiempo real con ngx-graph
  - **Terminal integrada** para compilación/ejecución
  - **Autoguardado** al cambiar de archivo
  - Soporte para Java y C++

### **4. Dialogs (Modales)**

#### **ShowclassComponent**
- Visualizar clase con atributos y métodos
- Diferenciar entre propios, heredados y no accesibles
- Ver código de funciones
- Agregar atributos/funciones/herencia
- Eliminar clase

#### **FormularioComponent**
- Crear nueva clase en el proyecto
- Seleccionar nivel de acceso
- Genera archivo .java o .cpp

#### **EditarFormularioComponent**
- Agregar atributos a clase existente
- Agregar funciones a clase existente
- Establecer herencia entre clases

#### **FormProyectComponent**
- Crear nuevo proyecto
- Seleccionar lenguaje (Java/C++)

### **5. Dashboard (Administrador)**
- **Componente**: `DashboardComponent`
- **Funcionalidad**:
  - Ver métricas de uso de la plataforma
  - Estadísticas de estudiantes
  - Análisis de logs de actividad
  - Gráficas con Chart.js

### **6. Hacer Examen**
- **Componente**: `HacerExamenComponent`
- **Funcionalidad**:
  - Listar exámenes disponibles
  - Realizar examen con temporizador
  - Guardar respuestas
  - Ver resultados y calificación

### **7. Realizar Test**
- **Componente**: `RealizarTestComponent`
- **Funcionalidad**:
  - Tests de práctica
  - Retroalimentación inmediata

---

## 🔐 Seguridad

### Frontend
- **Encriptación**: Crypto-JS para datos sensibles en localStorage
- **Guards**: AuthGuard protege rutas privadas
- **SecureStorageService**: Servicio para almacenamiento encriptado

### Backend
- **Autenticación**: Django session-based + AbstractBaseUser
- **CORS**: Configurado para permitir frontend en localhost:4200
- **CSRF**: Protección habilitada
- **Passwords**: Hashing con Django's built-in PBKDF2

---

## 📊 Recolección de Datos (Learning Analytics)

### Eventos Registrados

#### **Tooltips**
```python
LogActividad {
    usuario: "username",
    accion: "public" | "class" | "extends" | ... (keyword),
    detalle: lenguaje (java/cpp),
    fecha: timestamp
}
```

#### **Acciones del Editor**
- `MOSTRAR_DIAGRAMA`
- `OCULTAR_DIAGRAMA`
- `INTENTO_PEGAR` (anti-plagio)

#### **Compilación**
- Timestamp de compilación
- Resultado (éxito/error)
- Output del compilador

### Datos Demográficos del Usuario
- Género
- Edad
- Nivel socioeconómico
- Semestre actual

### Propósito
- **Predicción de rendimiento** con ML (scikit-learn)
- **Comparación**: Aprendizaje con POOGraph vs Tradicional
- **Identificación de patrones** de dificultad
- **Mejora continua** de la herramienta

---

## 🚀 Instalación y Despliegue

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar el repositorio
cd POOGRAPH

# Levantar todos los servicios
docker-compose up -d

# Acceder a:
# - Frontend: http://localhost:4200
# - Backend: http://localhost:8000
# - MySQL: localhost:3307
```

### Opción 2: Desarrollo Local

#### Backend
```bash
cd backend_tesis

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements-docker.txt

# Configurar base de datos en settings.py
# Ejecutar migraciones (si managed=True)
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

#### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
ng serve

# Acceder a http://localhost:4200
```

### Configuración de Base de Datos

**MySQL**:
```sql
CREATE DATABASE clases;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON clases.* TO 'root'@'localhost';
```

**Backend settings.py**:
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

---

## 🧪 Compilación y Ejecución de Código

### Proceso
1. Usuario escribe código en editor Monaco
2. Al hacer clic en "Ejecutar":
   - Se guarda el archivo actual
   - Backend recibe petición POST a `/compilar-proyecto`
   - Backend compila todos los archivos .java del proyecto
   - Si hay errores, retorna el output del compilador
   - Si compila, ejecuta la clase Main
   - Retorna output de la ejecución

### Compiladores Requeridos en el Servidor
- **Java**: JDK 11+ (`javac`, `java`)
- **C++**: g++ (MinGW en Windows, gcc en Linux)

---

## 🎓 Características Educativas

### 1. **Tooltips Interactivos**
- Doble clic en keywords muestra explicación
- Diferencia entre Java y C++
- Se registra automáticamente para analytics

### 2. **Anti-Plagio**
- Pegado de código bloqueado (Ctrl+V, Shift+Insert)
- Se registran intentos de pegado

### 3. **Visualización UML**
- Diagrama de clases en tiempo real
- Flechas de herencia automáticas
- Layout jerárquico (TB)

### 4. **Exámenes Evaluativos**
- Preguntas de opción múltiple
- Temporizador automático
- Calificación instantánea
- Historial de intentos

---

## 📈 Mejoras Futuras

- [ ] Soporte para interfaces en diagrama UML
- [ ] Colaboración en tiempo real (WebSockets)
- [ ] Integración con GitHub
- [ ] Análisis predictivo con ML (predicción de rendimiento)
- [ ] Sugerencias de código con IA
- [ ] Modo offline con PWA
- [ ] Soporte para más lenguajes (Python, C#)
- [ ] Tests unitarios automatizados
- [ ] Coverage de código

---

## 👥 Contribuidores

**Proyecto de Tesis**  
Universidad Autónoma de Aguascalientes  
Programa: Ingeniería en Sistemas Computacionales

---

## 📄 Licencia

Este proyecto es parte de una investigación académica.

