# 📐 Diagrama de Módulos - POOGraph

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────┐
│                          POOGRAPH SYSTEM                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    FRONTEND (Angular 13)                     │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │  │
│  │  │  Auth Module   │  │  Projects      │  │   Workspace   │ │  │
│  │  │                │  │  Module        │  │   Module      │ │  │
│  │  │ • Login        │  │ • Home         │  │ • Editor      │ │  │
│  │  │ • Register     │  │ • Create       │  │ • Diagram     │ │  │
│  │  │ • Guards       │  │ • List         │  │ • Terminal    │ │  │
│  │  └────────────────┘  └────────────────┘  └───────────────┘ │  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │  │
│  │  │  Class Module  │  │  Exam Module   │  │  Dashboard    │ │  │
│  │  │                │  │                │  │  Module       │ │  │
│  │  │ • Create       │  │ • List         │  │ • Analytics   │ │  │
│  │  │ • Edit         │  │ • Take Exam    │  │ • Charts      │ │  │
│  │  │ • Show Detail  │  │ • Results      │  │ • Reports     │ │  │
│  │  └────────────────┘  └────────────────┘  └───────────────┘ │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │              Services Layer                          │  │  │
│  │  │                                                       │  │  │
│  │  │  • BaseDeDatosService  • PrismService               │  │  │
│  │  │  • ProyectosService    • CodeService                │  │  │
│  │  │  • SecureStorageService • AutoLogoutService         │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│                              ↕ HTTP/REST API                        │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   BACKEND (Django 5.2)                       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │                Core Application                      │  │  │
│  │  │                                                       │  │  │
│  │  │  • Views (API Endpoints)                            │  │  │
│  │  │  • Models (ORM)                                     │  │  │
│  │  │  • Serializers                                      │  │  │
│  │  │  • URL Routing                                      │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │  │
│  │  │ Auth System    │  │ File Manager   │  │  Compiler     │ │  │
│  │  │                │  │                │  │  Module       │ │  │
│  │  │ • Login        │  │ • Read         │  │ • Javac       │ │  │
│  │  │ • Logout       │  │ • Write        │  │ • G++         │ │  │
│  │  │ • Sessions     │  │ • List         │  │ • Execute     │ │  │
│  │  └────────────────┘  └────────────────┘  └───────────────┘ │  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │  │
│  │  │ Parser Module  │  │ Logger Module  │  │  Exam System  │ │  │
│  │  │                │  │                │  │               │ │  │
│  │  │ • Javalang     │  │ • Activity Log │  │ • Questions   │ │  │
│  │  │ • AST          │  │ • Tooltip Log  │  │ • Options     │ │  │
│  │  │ • Extraction   │  │ • CSV Export   │  │ • Grading     │ │  │
│  │  └────────────────┘  └────────────────┘  └───────────────┘ │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│                              ↕ MySQL Driver                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   DATABASE (MySQL 8.0)                       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  • usuario            • proyecto          • clase           │  │
│  │  • atributos          • funciones         • herencia        │  │
│  │  • log_actividad      • examen            • pregunta        │  │
│  │  • opcion             • intento_examen    • respuesta       │  │
│  │                                                              │  │
│  │  Views:                                                      │  │
│  │  • herenciaf          • getatributos      • getfunciones    │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   FILE SYSTEM                                │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  • codigos_fuente/    → Archivos .java/.cpp de estudiantes  │  │
│  │  • archivos/          → Imágenes de diagramas               │  │
│  │  • datos/             → CSVs de logs de actividad           │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Módulos del Frontend

### **1. Auth Module**
**Ubicación**: `src/app/login/`, `src/app/register/`, `src/app/guards/`

**Componentes:**
- `LoginComponent`: Formulario de inicio de sesión
- `RegisterComponent`: Formulario de registro con datos demográficos
- `AuthGuard`: Protección de rutas privadas

**Servicios:**
- `SecureStorageService`: Encriptación de datos en localStorage
- `AutoLogoutService`: Cierre de sesión automático por inactividad

**Funcionalidades:**
- Login/Logout con sesiones
- Registro de nuevos estudiantes
- Almacenamiento seguro de tokens
- Redirección automática

---

### **2. Projects Module (Home)**
**Ubicación**: `src/app/home/`, `src/app/dialogs/form-proyect/`

**Componentes:**
- `HomeComponent`: Lista de proyectos del usuario
- `FormProyectComponent`: Modal para crear proyecto

**Servicios:**
- `ProyectosService`: CRUD de proyectos

**Funcionalidades:**
- Listar proyectos del usuario
- Crear nuevo proyecto (Java/C++)
- Eliminar proyecto
- Navegar al workspace

---

### **3. Workspace Module (Área de Trabajo)**
**Ubicación**: `src/app/area-de-trabajo/`

**Componentes:**
- `AreaDeTrabajoComponent`: Editor principal con 3 paneles

**Subcomponentes:**
- **Explorador de Archivos**: Lista de clases del proyecto
- **Editor Monaco**: Editor de código profesional
- **Diagrama UML**: Visualización con ngx-graph
- **Terminal**: Consola de salida

**Servicios:**
- `CodeService`: Gestión de archivos y compilación
- `PrismService`: Syntax highlighting

**Funcionalidades:**
- Escribir código con autocompletado
- Cambiar entre archivos (con autoguardado)
- Ver diagrama UML en tiempo real
- Tooltips educativos por doble clic
- Bloqueo de pegado (anti-plagio)
- Compilar y ejecutar proyectos
- Ver errores de compilación

**Características Especiales:**
- Tema personalizado "POOGraph Dark"
- Registro automático de tooltips consultados
- Entrada de usuario para programas interactivos

---

### **4. Class Module (Gestión de Clases)**
**Ubicación**: `src/app/dialogs/`

**Componentes:**
- `ShowclassComponent`: Modal con detalles de clase
- `FormularioComponent`: Modal para crear clase
- `EditarFormularioComponent`: Modal para editar clase

**Servicios:**
- `BaseDeDatosService`: API de clases, atributos, funciones

**Funcionalidades:**
- Crear nueva clase
- Ver atributos propios/heredados/no accesibles
- Ver métodos propios/heredados/no accesibles
- Agregar atributo (inyección en código)
- Agregar función (inyección en código)
- Establecer herencia (modifica extends)
- Eliminar clase (excepto Main)
- Ver código de funciones heredadas

---

### **5. Exam Module**
**Ubicación**: `src/app/hacer-examen/`, `src/app/realizar-test/`

**Componentes:**
- `HacerExamenComponent`: Lista y realización de exámenes
- `RealizarTestComponent`: Tests de práctica

**Funcionalidades:**
- Listar exámenes disponibles
- Iniciar intento de examen
- Temporizador automático
- Navegación entre preguntas
- Envío de respuestas
- Ver resultados y calificación

---

### **6. Dashboard Module (Solo Profesores)**
**Ubicación**: `src/app/dashboard/`

**Componentes:**
- `DashboardComponent`: Panel de métricas

**Librerías:**
- Chart.js: Gráficas interactivas

**Funcionalidades:**
- Ver usuarios activos
- Proyectos creados
- Tooltips más consultados
- Tiempo promedio de sesión
- Rendimiento por estudiante
- Gráficas de tendencias

---

### **7. Shared Components**
**Ubicación**: `src/app/dialogs/`

**Componentes:**
- `ConfirmComponent`: Modal de confirmación
- `ErrorComponent`: Modal de error
- `NavbarComponent`: Barra de navegación

---

## 🔧 Servicios del Frontend

### **BaseDeDatosService**
```typescript
// Gestión de entidades principales
getClasesProyectId(idProyecto): Observable
getClaseId(id): Observable
crearClase(clase): Observable
deleteClase(id): Observable
getInfoCompletaClase(idClase): Observable
getCodigoFuncion(idClase, nombre, tipo): Observable
```

### **ProyectosService**
```typescript
// CRUD de proyectos
crearProyecto(proyecto): Observable
getProyectosUsuario(idUsuario): Observable
getProyectoIndividual(nombre, idUsuario): Observable
```

### **CodeService**
```typescript
// Gestión de código fuente
obtenerCodigoFuente(idClase): Observable
listarArchivos(idProyecto): Observable
leerArchivoPorRuta(rutaRelativa): Observable
guardarArchivo(ruta, contenido, idProyecto): Observable
compilarProyecto(idProyecto, entradas): Observable
registrarTooltip(idUsuario, palabra, lenguaje): Observable
```

### **SecureStorageService**
```typescript
// Almacenamiento encriptado
setItem(key, value): void
getItem(key): string
removeItem(key): void
clear(): void
```

---

## ⚙️ Módulos del Backend

### **1. Core Application**
**Ubicación**: `backend_tesis/core/`

**Archivos Principales:**
- `models.py`: 15+ modelos ORM
- `views.py`: 30+ endpoints API
- `admin.py`: Configuración del admin de Django

---

### **2. Authentication System**

**Modelo:**
- `Usuario (AbstractBaseUser)`: Modelo personalizado con campos demográficos

**Endpoints:**
```python
POST /api/login/       # Autenticación
POST /api/logout/      # Cierre de sesión
POST /api/register/    # Registro
```

**Características:**
- Hashing de contraseñas con PBKDF2
- Sesiones de Django
- Campos demográficos para investigación

---

### **3. File Manager Module**

**Funcionalidades:**
- Leer archivos del sistema de archivos
- Escribir cambios en archivos
- Listar archivos de un proyecto
- Crear nuevos archivos

**Endpoints:**
```python
GET  /archivos-proyecto/<proyecto_id>
POST /leer-archivo
POST /guardar-archivo
POST /upload
```

**Directorios:**
- `codigos_fuente/`: Código de estudiantes organizado por proyecto
- `archivos/`: Imágenes de diagramas UML

---

### **4. Compiler Module**

**Funcionalidades:**
- Compilar proyectos Java con `javac`
- Compilar proyectos C++ con `g++`
- Ejecutar y capturar salida
- Manejar errores de compilación
- Soporte para entrada de usuario

**Endpoint:**
```python
POST /compilar-proyecto
```

**Proceso:**
1. Recibe ID de proyecto
2. Busca todos los archivos .java o .cpp
3. Compila con el compilador apropiado
4. Si hay errores, retorna output
5. Si compila, ejecuta Main
6. Retorna salida estándar/error

---

### **5. Parser Module**

**Librería:** `javalang`

**Funcionalidades:**
- Parsear código Java a AST
- Extraer clases, atributos, métodos
- Determinar niveles de acceso
- Extraer código de funciones específicas
- Detectar relaciones de herencia

**Usado por:**
- `obtener_info_completa_clase()`
- `obtener_codigo_funcion()`

---

### **6. Logger Module**

**Modelos:**
- `LogActividad`: Log general de acciones

**Endpoint:**
```python
POST /api/tooltip-log
```

**Tipos de Logs:**
- **Tooltips consultados**: Palabra clave, lenguaje, timestamp
- **Intentos de pegado**: Evento anti-plagio
- **Toggle de diagrama**: Mostrar/ocultar
- **Compilaciones**: Éxito/fracaso

**Almacenamiento:**
- Base de datos MySQL
- Exportación a CSV para análisis (pandas)

---

### **7. Exam System Module**

**Modelos:**
- `Examen`
- `Pregunta`
- `Opcion`
- `IntentoExamen`
- `RespuestaEstudiante`

**Endpoints:**
```python
POST /examenes/crear
GET  /examenes
GET  /examenes/disponibles/<id_estudiante>
GET  /examenes/<id_examen>/estudiante
POST /examenes/iniciar
POST /examenes/enviar
GET  /examenes/resultados/<id_intento>
```

**Funcionalidades:**
- Crear exámenes con preguntas de opción múltiple
- Listar exámenes disponibles por fecha
- Iniciar intento (timestamp)
- Guardar respuestas
- Calificar automáticamente
- Mostrar resultados

---

### **8. Analytics Module**

**Endpoint:**
```python
GET /api/dashboard-analytics
```

**Métricas Calculadas:**
- Total de usuarios registrados
- Proyectos creados (Java vs C++)
- Tooltips más consultados (Top 10)
- Actividad por día (últimos 7 días)
- Rendimiento promedio en exámenes

**Uso:** Dashboard de profesores

---

## 🗄️ Base de Datos

### **Tablas Principales**

#### **Usuarios y Proyectos**
```
usuario ─┬─< proyecto ─┬─< clase ─┬─< atributos
         │             │          └─< funciones
         │             └─< clase ─┬─< atributos
         │                        └─< funciones
         └─< examen ─< pregunta ─< opcion
```

#### **Herencia**
```
clase (padre) ─< herencia >─ clase (hijo)
```

#### **Exámenes**
```
usuario (estudiante) ─< intento_examen ─< respuesta_estudiante
                              │
examen ─< pregunta ─< opcion  │
                              │
                     respuesta_estudiante >─ opcion
```

### **Vistas**
- `herenciaf`: Relaciones de herencia con nombres
- `getatributos`: Atributos con nombre de clase
- `getfunciones`: Funciones con nombre de clase

---

## 🔄 Flujos Principales

### **Flujo 1: Crear Proyecto**
```
Usuario → HomeComponent → FormProyectComponent → ProyectosService
            ↓
        POST /proyecto (Backend)
            ↓
        Inserta en tabla `proyecto`
            ↓
        Crea directorio en `codigos_fuente/`
            ↓
        Crea archivo Main.java
            ↓
        Inserta clase Main en BD
            ↓
        Retorna proyecto creado
```

### **Flujo 2: Escribir y Ejecutar Código**
```
Usuario escribe en Monaco Editor
            ↓
Usuario cambia de archivo
            ↓
AreaDeTrabajoComponent.abrirArchivo()
            ↓
CodeService.guardarArchivo() (archivo anterior)
            ↓
Backend: POST /guardar-archivo
            ↓
Actualiza archivo en codigos_fuente/
            ↓
CodeService.leerArchivoPorRuta() (archivo nuevo)
            ↓
Carga código en editor

───────────────────────────────

Usuario hace clic en "Ejecutar"
            ↓
CodeService.compilarProyecto()
            ↓
Backend: POST /compilar-proyecto
            ↓
Ejecuta javac *.java
            ↓
Si hay errores → Retorna errores
            ↓
Si compila → Ejecuta java Main
            ↓
Retorna output
            ↓
Muestra en Terminal
```

### **Flujo 3: Agregar Atributo**
```
Usuario clic en clase del diagrama
            ↓
ShowclassComponent se abre
            ↓
Usuario clic "Agregar Atributo"
            ↓
EditarFormularioComponent (modal)
            ↓
Usuario completa formulario
            ↓
POST /atributos
            ↓
Backend:
  1. Inserta en tabla `atributos`
  2. Lee archivo .java de la clase
  3. Inyecta declaración del atributo
  4. Guarda archivo modificado
            ↓
Cierra modal
            ↓
ShowclassComponent.cargarInfoCompleta()
            ↓
Actualiza vista
```

### **Flujo 4: Tooltip Educativo**
```
Usuario hace doble clic en keyword
            ↓
AreaDeTrabajoComponent.registrarDobleClicTooltip()
            ↓
Busca keyword en tooltipKeywords{}
            ↓
Muestra widget en editor
            ↓
CodeService.registrarTooltip()
            ↓
POST /api/tooltip-log
            ↓
Inserta en tabla `log_actividad`
            ↓
(Analizado después por Dashboard)
```

---

## 📊 Tecnologías por Capa

### **Frontend**
| Propósito | Tecnología |
|-----------|-----------|
| Framework | Angular 13.3 |
| Lenguaje | TypeScript 4.6 |
| Editor de Código | Monaco Editor |
| Diagrama UML | @swimlane/ngx-graph, D3.js, Dagre |
| UI Components | Angular Material |
| Gráficas | Chart.js, ng2-charts |
| Seguridad | Crypto-JS (AES) |
| HTTP Client | @angular/common/http |
| Routing | @angular/router |

### **Backend**
| Propósito | Tecnología |
|-----------|-----------|
| Framework | Django 5.2 |
| API | Django REST Framework |
| Base de Datos | MySQL 8.0 |
| ORM | Django ORM |
| CORS | django-cors-headers |
| Parser | javalang (AST) |
| Data Science | pandas, numpy, scikit-learn |

### **DevOps**
| Propósito | Tecnología |
|-----------|-----------|
| Contenedorización | Docker, Docker Compose |
| Frontend Server | Nginx |
| Backend Server | Gunicorn/Uvicorn |
| Orquestación | docker-compose.yml |

---

## 🔐 Seguridad por Módulo

### **Frontend**
- **SecureStorageService**: AES-256 encryption para localStorage
- **AuthGuard**: Protección de rutas
- **Token Validation**: Verificación en cada petición

### **Backend**
- **Django Sessions**: Manejo seguro de sesiones
- **CORS**: Configuración restrictiva
- **CSRF Protection**: Habilitada
- **Password Hashing**: PBKDF2 SHA-256
- **SQL Injection**: Prevención con ORM

### **Database**
- **Prepared Statements**: Vía Django ORM
- **Constraints**: Foreign keys, unique together
- **Backups**: (Configurar según entorno)

---

## 📈 Escalabilidad

### **Frontend**
- **Lazy Loading**: Módulos cargados bajo demanda
- **AOT Compilation**: Build optimizado para producción
- **Tree Shaking**: Eliminación de código no usado

### **Backend**
- **Connection Pooling**: MySQL con mysqlclient
- **Caching**: (Implementar con Redis si es necesario)
- **Async Views**: Soporte para operaciones I/O

### **Database**
- **Indexes**: En foreign keys y campos frecuentes
- **Views**: Para queries complejas repetitivas
- **Normalization**: 3NF aplicada

---

*Este diagrama representa la arquitectura actual de POOGraph (Julio 2026)*

