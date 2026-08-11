# 📚 Índice de Documentación - POOGraph

## Documentos Disponibles

### 1. 📘 README Principal
**Archivo**: `README_POOGRAPH.md`

Introducción general al proyecto con:
- Descripción del sistema
- Características principales
- Arquitectura general
- Instalación rápida (Docker)
- Instalación manual (desarrollo)
- Endpoints principales
- Troubleshooting básico
- Roadmap

**Para**: Nuevos desarrolladores, usuarios, administradores

---

### 2. 🔧 Documentación Técnica Completa
**Archivo**: `DOCUMENTACION_TECNICA_POOGRAPH.md`

Documentación técnica exhaustiva con:
- Stack tecnológico detallado
- Estructura completa del proyecto
- Modelo de base de datos (15+ tablas)
- API Endpoints (30+ rutas)
- Módulos del frontend (7 módulos)
- Módulos del backend (8 módulos)
- Seguridad y autenticación
- Learning analytics
- Compilación de código
- Características educativas

**Para**: Desarrolladores, arquitectos de software, mantenedores

---

### 3. 👨‍🎓 Manual de Usuario
**Archivo**: `MANUAL_USUARIO_POOGRAPH.md`

Manual completo para estudiantes y profesores con:
- Registro e inicio de sesión
- Crear y gestionar proyectos
- Uso del editor de código
- Visualización de diagramas UML
- Compilar y ejecutar programas
- Tooltips educativos
- Sistema de exámenes
- Dashboard de analytics (profesores)
- FAQ y solución de problemas
- Consejos y buenas prácticas

**Para**: Estudiantes, profesores, usuarios finales

---

### 4. 📐 Diagrama de Módulos
**Archivo**: `DIAGRAMA_MODULOS_POOGRAPH.md`

Arquitectura visual del sistema con:
- Diagrama de arquitectura general
- Módulos del frontend (detallados)
- Módulos del backend (detallados)
- Modelo de base de datos
- Flujos principales del sistema
- Tecnologías por capa
- Seguridad por módulo
- Escalabilidad

**Para**: Arquitectos, desarrolladores senior, analistas

---

### 5. 👨‍💻 Guía de Desarrollo
**Archivo**: `GUIA_DESARROLLO_POOGRAPH.md`

Mejores prácticas y patrones con:
- Convenciones de código (TypeScript y Python)
- Estructura de componentes
- Gestión de estado
- API y servicios
- Testing (unit, integration, E2E)
- Debugging (frontend y backend)
- Optimización de performance
- Deployment y CI/CD

**Para**: Desarrolladores activos, contribuidores

---

## 🗂️ Organización de los Documentos

```
POOGRAPH/
│
├── README.md                            # ← README_POOGRAPH.md (copiar aquí)
│
├── docs/                                # ← Crear esta carpeta
│   ├── DOCUMENTACION_TECNICA.md
│   ├── MANUAL_USUARIO.md
│   ├── DIAGRAMA_MODULOS.md
│   ├── GUIA_DESARROLLO.md
│   └── INDICE_DOCUMENTACION.md (este archivo)
│
├── backend_tesis/
│   └── README.md                        # Instrucciones específicas del backend
│
└── frontend/
    └── README.md                        # Instrucciones específicas del frontend
```

---

## 📖 Recomendaciones de Lectura

### Para Comenzar Rápido
1. **README Principal** - Instalación y overview
2. **Manual de Usuario** - Si eres estudiante/profesor

### Para Desarrollar
1. **README Principal** - Setup del entorno
2. **Guía de Desarrollo** - Convenciones y patrones
3. **Documentación Técnica** - Referencia de API

### Para Contribuir
1. **Documentación Técnica** - Entender el sistema
2. **Diagrama de Módulos** - Visualizar arquitectura
3. **Guía de Desarrollo** - Seguir estándares

### Para Investigación
1. **Documentación Técnica** - Sección "Learning Analytics"
2. **Manual de Usuario** - Características educativas
3. **Diagrama de Módulos** - Flujos de recolección de datos

---

## 🔄 Actualización de Documentación

### Cuándo Actualizar

- ✅ **Nuevas features**: Agregar a Documentación Técnica + Manual Usuario
- ✅ **Cambios en API**: Actualizar Documentación Técnica
- ✅ **Nuevos módulos**: Actualizar Diagrama de Módulos
- ✅ **Cambios en setup**: Actualizar README Principal
- ✅ **Nuevas convenciones**: Actualizar Guía de Desarrollo

### Formato de Cambios

```markdown
## Versión X.Y (Fecha)

### Agregado
- Nueva funcionalidad Z

### Modificado
- Cambio en módulo W

### Eliminado
- Feature antigua Y

### Corregido
- Bug en componente X
```

---

## 📝 Plantillas

### Para Agregar Nueva Feature

```markdown
## Nombre de la Feature

### Descripción
[Breve descripción]

### Ubicación
- **Frontend**: `src/app/modulo/componente.ts`
- **Backend**: `core/views.py` (función `nombre_funcion`)

### Endpoints
```
POST /api/nueva-ruta
GET  /api/consultar
```

### Uso
```typescript
// Ejemplo de código
```

### Screenshots
![Screenshot](ruta/imagen.png)
```

---

## 🤝 Contribuyendo a la Documentación

1. **Identifica** qué documento necesita actualización
2. **Edita** siguiendo el formato Markdown existente
3. **Revisa** ortografía y formato
4. **Prueba** los ejemplos de código
5. **Commit** con mensaje descriptivo: `docs: actualizar sección X en DOCUMENTO.md`

---

## 📞 Soporte

Si encuentras errores en la documentación o tienes sugerencias:
- Abre un **Issue** con la etiqueta `documentation`
- Propón cambios con un **Pull Request**

---

## 📊 Estado de la Documentación

| Documento | Estado | Última Actualización | Completitud |
|-----------|--------|---------------------|-------------|
| README Principal | ✅ Completo | Julio 2026 | 100% |
| Documentación Técnica | ✅ Completo | Julio 2026 | 100% |
| Manual de Usuario | ✅ Completo | Julio 2026 | 100% |
| Diagrama de Módulos | ✅ Completo | Julio 2026 | 100% |
| Guía de Desarrollo | ✅ Completo | Julio 2026 | 100% |

---

## 🎯 Próximos Pasos

- [ ] Agregar diagramas visuales (UML, secuencia)
- [ ] Video tutoriales enlazados
- [ ] Documentación de API con Swagger/OpenAPI
- [ ] Ejemplos de código completos en repositorio
- [ ] Troubleshooting expandido con casos reales
- [ ] Traducción al inglés

---

**Documentación generada para el proyecto POOGraph**  
*Universidad Autónoma de Aguascalientes*  
*Julio 2026*

