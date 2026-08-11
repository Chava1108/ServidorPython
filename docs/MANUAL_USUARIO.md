# 📖 Manual de Usuario - POOGraph

## 🎯 ¿Qué es POOGraph?

**POOGraph** es una plataforma educativa interactiva diseñada para ayudarte a aprender **Programación Orientada a Objetos (POO)** de forma visual y práctica. Con POOGraph puedes:

- ✍️ Escribir código Java o C++ en un editor profesional
- 👁️ Ver tus clases representadas en diagramas UML en tiempo real
- ▶️ Compilar y ejecutar tus programas directamente en el navegador
- 📚 Aprender conceptos de POO con tooltips educativos
- ✅ Realizar exámenes evaluativos
- 📊 Seguir tu progreso de aprendizaje

---

## 🚀 Comenzando

### 1. Registro de Usuario

1. Abre tu navegador y ve a: `http://localhost:4200` (o la URL que te proporcione tu profesor)
2. Haz clic en **"Registrarse"**
3. Completa el formulario:
   - **Nombre completo**
   - **Correo electrónico**
   - **Nombre de usuario** (único)
   - **Contraseña**
   - **Género** (Masculino, Femenino, Otro)
   - **Edad**
   - **Nivel socioeconómico**
   - **Semestre actual**

4. Haz clic en **"Registrar"**

> ℹ️ **Nota**: Estos datos son importantes para el estudio de investigación y se mantienen completamente anónimos.

### 2. Iniciar Sesión

1. En la página de inicio, ingresa tu **usuario** y **contraseña**
2. Haz clic en **"Iniciar Sesión"**
3. Serás redirigido a tu **Espacio de Trabajo**

---

## 🏠 Pantalla Principal (Home)

### Vista de Proyectos

Después de iniciar sesión, verás la lista de tus proyectos de programación.

#### **Crear un Nuevo Proyecto**

1. Haz clic en el botón **"+ Nuevo Proyecto"**
2. Completa el formulario:
   - **Nombre del proyecto**: Ej. "MiPrimerProyecto"
   - **Lenguaje**: Selecciona **Java** o **C++**
3. Haz clic en **"Crear"**
4. El proyecto aparecerá en tu lista con una clase inicial llamada **Main**

#### **Abrir un Proyecto**

1. Haz clic en el proyecto que deseas abrir
2. Haz clic en **"Abrir"** o **"Ver código"**
3. Serás redirigido al **Área de Trabajo**

#### **Eliminar un Proyecto**

1. Haz clic en el ícono de **eliminar** (🗑️) junto al proyecto
2. Confirma la eliminación

---

## 🖥️ Área de Trabajo (Editor Principal)

Esta es la pantalla más importante de POOGraph. Aquí escribes código, ves tu diagrama y ejecutas tus programas.

### Distribución de la Pantalla

```
┌─────────────────────────────────────────────────────────┐
│  [Navbar]  Proyecto: MiProyecto         [Ejecutar] [⚙️]│
├───────────┬─────────────────────┬───────────────────────┤
│           │                     │                       │
│ Explorador│   Editor de Código  │   Diagrama UML        │
│ Archivos  │   (Monaco Editor)   │   (ngx-graph)         │
│           │                     │                       │
│ Main.java │   public class...   │     ┌────────┐        │
│ Persona   │                     │     │  Main  │        │
│ Alumno    │                     │     └────────┘        │
│           │                     │         ↑             │
│           │                     │         │             │
│           │                     │     ┌────────┐        │
│           │                     │     │Persona │        │
│           │                     │     └────────┘        │
├───────────┴─────────────────────┴───────────────────────┤
│  Terminal / Consola                                     │
│  > Compilando...                                        │
│  > ✅ Compilación exitosa                               │
└─────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### **1. Explorador de Archivos (Izquierda)**

Muestra todos los archivos `.java` o `.cpp` de tu proyecto.

- **Clic en un archivo**: Lo abre en el editor
- **Main.java**: Clase principal (no se puede eliminar)
- **Clases secundarias**: Clases que has creado

#### **2. Editor de Código (Centro)**

Editor profesional **Monaco Editor** (el mismo de Visual Studio Code).

**Características:**
- ✨ Syntax highlighting (colores para palabras clave)
- 🔍 Autocompletado de código
- 📏 Números de línea
- 🎨 Tema oscuro personalizado "POOGraph Dark"
- 💡 Tooltips educativos (ver sección Tooltips)
- 🚫 Pegado deshabilitado (para fomentar el aprendizaje)

**Atajos de Teclado:**
- `Ctrl + S`: No disponible (guarda automáticamente al cambiar de archivo)
- `Ctrl + F`: Buscar en el código
- `Ctrl + H`: Buscar y reemplazar
- `Ctrl + Z`: Deshacer
- `Ctrl + Y`: Rehacer
- `Tab`: Indentar
- `Shift + Tab`: Des-indentar

#### **3. Diagrama UML (Derecha)**

Visualización gráfica de tus clases en tiempo real.

**Elementos del Diagrama:**
- 📦 **Nodos**: Cada clase aparece como una caja con su nombre
- ➡️ **Flechas**: Muestran relaciones de herencia (extends)
- 🔄 **Auto-actualización**: Se actualiza cuando guardas cambios

**Interacciones:**
- **Clic en un nodo**: Abre el modal con detalles de la clase
- **Arrastrar nodos**: Reorganiza el diagrama
- **Zoom**: Con la rueda del mouse

#### **4. Terminal / Consola (Abajo)**

Muestra la salida de tus programas y mensajes del sistema.

**Tipos de mensajes:**
- ℹ️ **Info** (azul): Mensajes informativos
- ❌ **Error** (rojo): Errores de compilación/ejecución
- ✅ **Éxito** (verde): Operaciones exitosas

---

## ✍️ Escribiendo Código

### Crear una Nueva Clase

#### **Opción 1: Desde el Diagrama**

1. Haz clic derecho en el área del diagrama (lado derecho)
2. Selecciona **"Nueva Clase"**
3. Completa el formulario:
   - **Nombre de la clase**: Ej. "Persona" (sin espacios, PascalCase)
   - **Nivel de acceso**: public, private, protected
4. Haz clic en **"Crear"**
5. La clase aparecerá en el explorador de archivos y en el diagrama

#### **Opción 2: Desde el Navbar**

1. Haz clic en el botón **"+ Agregar Clase"** en la barra superior
2. Sigue los mismos pasos anteriores

### Editar una Clase

1. En el **Explorador de Archivos**, haz clic en el archivo que deseas editar
2. El código aparecerá en el **Editor**
3. Escribe tu código normalmente
4. **Cambiar de archivo guarda automáticamente** el archivo actual

> ⚠️ **Importante**: Al cambiar de un archivo a otro, los cambios se guardan automáticamente. No necesitas hacer "Guardar".

### Ver Detalles de una Clase

1. Haz clic en un nodo del **Diagrama UML**
2. Se abrirá un modal que muestra:

**Sección de Atributos:**
- ✅ **Atributos Propios**: Los que definiste en esta clase
- 🔗 **Atributos Heredados**: Los que vienen de la clase padre
- 🚫 **No Accesibles**: Atributos privados del padre

**Sección de Métodos:**
- ✅ **Métodos Propios**
- 🔗 **Métodos Heredados**
- 🚫 **No Accesibles**

**Acciones disponibles:**
- ➕ **Agregar Atributo**: Añade un nuevo campo a la clase
- ➕ **Agregar Función**: Añade un nuevo método a la clase
- 🔗 **Agregar Herencia**: Establece una clase padre
- 🗑️ **Eliminar Clase**: Elimina la clase (excepto Main)

#### **Agregar Atributo**

1. Clic en **"Agregar Atributo"**
2. Completa:
   - **Nombre**: Ej. "nombre"
   - **Tipo**: String, int, double, boolean, etc.
   - **Nivel**: public, private, protected
3. El atributo se inserta automáticamente en el código

#### **Agregar Método/Función**

1. Clic en **"Agregar Función"**
2. Completa:
   - **Nombre**: Ej. "calcularEdad"
   - **Tipo de retorno**: void, int, String, etc.
   - **Nivel**: public, private, protected
   - **Parámetros** (opcional): Ej. "int año"
3. El método se inserta en el código con una plantilla básica

#### **Establecer Herencia**

1. Clic en **"Agregar Herencia"**
2. Selecciona la **Clase Padre** del dropdown
3. El código se actualiza con `extends ClasePadre`
4. Una flecha aparece en el diagrama UML

### Ver Código de un Método Heredado

1. En el modal de clase, ve a la sección **"Métodos Heredados"**
2. **Haz hover** sobre el método
3. Aparecerá un tooltip con el código fuente del método

---

## ▶️ Compilar y Ejecutar

### Ejecutar tu Programa

1. Asegúrate de que tu clase **Main** tenga un método `main`:
   ```java
   public static void main(String[] args) {
       // Tu código aquí
   }
   ```

2. Haz clic en el botón **"▶️ Ejecutar"** en la barra superior

3. POOGraph hará lo siguiente automáticamente:
   - Guarda todos los archivos
   - Compila todos los archivos del proyecto
   - Ejecuta la clase Main
   - Muestra la salida en la **Terminal**

### Errores de Compilación

Si tu código tiene errores de sintaxis:

```
❌ Error de compilación:
Main.java:5: error: ';' expected
    System.out.println("Hola")
                              ^
1 error
```

**Cómo solucionarlo:**
1. Lee el mensaje de error cuidadosamente
2. Identifica el **archivo** y **número de línea**
3. Corrige el error en el editor
4. Vuelve a ejecutar

### Entrada de Usuario

Si tu programa necesita entrada del usuario (Scanner en Java, cin en C++):

1. Antes de hacer clic en **"Ejecutar"**, ingresa los datos en el campo **"Entrada de Usuario"** en la terminal
2. Separa múltiples entradas con espacios o saltos de línea
3. Ejemplo:
   ```
   Juan
   25
   ```
4. Haz clic en **"Ejecutar"**
5. El programa usará esos datos como entrada

---

## 💡 Tooltips Educativos

POOGraph tiene un sistema de **ayuda contextual** para ayudarte a aprender POO.

### Cómo Usar los Tooltips

1. **Haz doble clic** en cualquier palabra clave del código:
   - `public`, `private`, `protected`
   - `class`, `extends`, `implements`
   - `static`, `final`, `abstract`
   - `if`, `for`, `while`
   - `int`, `String`, `boolean`
   - Y muchas más...

2. Aparecerá un **cuadro flotante** con:
   - 📘 **Explicación** del concepto
   - 💡 **Uso** y sintaxis
   - 🎓 **Buenas prácticas**

3. El tooltip se cierra automáticamente:
   - Al hacer clic en cualquier parte
   - Al presionar **Esc**
   - Después de 8 segundos

**Ejemplo:**

Al hacer doble clic en `extends`:

```
┌─────────────────────────────────────────┐
│  POOGraph - Ayuda                       │
├─────────────────────────────────────────┤
│  extends                                │
│                                         │
│  Indica que una clase hereda de otra   │
│  (clase padre). Java solo permite      │
│  herencia simple.                       │
│                                         │
│  Uso:                                   │
│    public class Alumno extends Persona  │
└─────────────────────────────────────────┘
```

> 📊 **Nota**: Cada tooltip que consultas se registra automáticamente para el estudio de investigación. Esto ayuda a entender qué conceptos son más difíciles para los estudiantes.

---

## 🚫 ¿Por Qué No Puedo Pegar Código?

POOGraph **deshabilita el pegado de código** (`Ctrl+V`, `Ctrl+Shift+V`, menú contextual) por las siguientes razones educativas:

1. **Fomenta el aprendizaje activo**: Escribir código manualmente te ayuda a memorizarlo
2. **Previene el plagio**: Asegura que el código sea tu propio trabajo
3. **Desarrolla muscle memory**: La escritura repetitiva mejora la retención
4. **Detecta dificultades**: Si intentas pegar, se registra para análisis

Si intentas pegar, verás el mensaje:

```
⚠️ Pegar código está deshabilitado. 
   Escribe tu código manualmente.
```

> 💡 **Consejo**: Usa los tooltips educativos si no recuerdas la sintaxis.

---

## 📚 Exámenes

### Ver Exámenes Disponibles

1. En el **Navbar**, haz clic en **"Exámenes"** o **"Hacer Examen"**
2. Verás la lista de exámenes disponibles:
   - Título del examen
   - Fecha disponible
   - Duración
   - Estado (Disponible / Completado)

### Realizar un Examen

1. Haz clic en **"Iniciar Examen"**
2. Lee las instrucciones cuidadosamente
3. Aparecerá un **temporizador** en la parte superior
4. Lee cada pregunta y selecciona la respuesta correcta
5. Puedes navegar entre preguntas con los botones **"Anterior"** / **"Siguiente"**
6. Al terminar, haz clic en **"Enviar Examen"**

> ⚠️ **Advertencia**: Una vez enviado, no puedes modificar tus respuestas.

### Ver Resultados

1. Después de enviar, verás tu **calificación** inmediatamente
2. Puedes revisar:
   - Respuestas correctas
   - Respuestas incorrectas
   - Explicaciones (si el profesor las agregó)

---

## 📊 Dashboard (Solo Profesores)

Si eres profesor o administrador, tendrás acceso al **Dashboard de Analytics**.

### Métricas Disponibles

- 📈 **Usuarios activos**
- 📚 **Proyectos creados**
- 🔍 **Tooltips más consultados** (conceptos difíciles)
- ⏱️ **Tiempo promedio de sesión**
- 🎯 **Tasa de completación de exámenes**
- 📊 **Rendimiento por estudiante**

### Cómo Acceder

1. Inicia sesión con una cuenta de profesor
2. En el **Navbar**, haz clic en **"Dashboard"**
3. Explora las diferentes secciones y gráficas

---

## 🔧 Consejos y Buenas Prácticas

### ✅ Mejores Prácticas de Código

1. **Nombres descriptivos**: `calcularPromedio()` es mejor que `calcular()`
2. **Indentación consistente**: Usa 4 espacios o 1 tab
3. **Comentarios útiles**: Explica el "por qué", no el "qué"
   ```java
   // ❌ Mal
   int x = 5; // asigna 5 a x
   
   // ✅ Bien
   int edadMinima = 5; // Edad mínima para inscripción
   ```
4. **Una clase, una responsabilidad**: No mezcles lógica de negocios con interfaz
5. **Encapsulamiento**: Usa `private` para atributos, `public` para métodos

### 🎯 Consejos para Aprender POO

1. **Piensa en objetos reales**: Una clase `Perro` puede tener atributos (`nombre`, `raza`) y métodos (`ladrar()`, `comer()`)
2. **Usa herencia cuando tenga sentido**: `Perro` y `Gato` pueden heredar de `Animal`
3. **Prueba tu código frecuentemente**: Ejecuta después de cada cambio pequeño
4. **Usa los tooltips**: No tengas miedo de hacer doble clic en palabras que no entiendas
5. **Experimenta**: Cambia valores, prueba diferentes enfoques

### 🚀 Atajos de Productividad

- Usa el **Explorador de Archivos** para navegar rápidamente entre clases
- El **Diagrama UML** te da una visión global del proyecto
- Si un archivo no se guarda, cambia de archivo y vuelve a abrirlo
- Limpia la terminal con el botón **"Limpiar"** para mejor legibilidad

---

## ❓ Preguntas Frecuentes (FAQ)

### **¿Puedo trabajar en varios proyectos a la vez?**
Sí, pero solo uno a la vez por sesión. Guarda tu trabajo y cierra el proyecto actual antes de abrir otro.

### **¿Mis proyectos se guardan automáticamente?**
Sí, al cambiar de archivo los cambios se guardan. Sin embargo, es buena idea hacer clic en **"Guardar"** antes de cerrar el navegador.

### **¿Puedo descargar mi código?**
Actualmente no hay opción de descarga directa. Puedes copiar manualmente el código (aunque no puedas pegar).

### **¿Puedo subir archivos externos?**
No, todos los archivos deben crearse dentro de POOGraph para garantizar la integridad del estudio.

### **¿Por qué no aparece mi clase en el diagrama?**
Asegúrate de que:
1. El archivo tenga la extensión correcta (`.java` o `.cpp`)
2. La clase tenga un modificador de acceso (`public class`)
3. Hayas guardado los cambios (cambia de archivo o haz clic en "Guardar")

### **¿Qué pasa si cierro el navegador sin guardar?**
Los cambios del archivo actualmente abierto pueden perderse. Siempre cambia a otro archivo antes de cerrar (esto fuerza el guardado).

### **¿Puedo usar librerías externas?**
Por ahora, solo las librerías estándar de Java (`java.util.*`) y C++ (`iostream`, `string`, etc.).

### **¿Cómo elimino una clase?**
1. Haz clic en el nodo de la clase en el diagrama
2. En el modal, haz clic en **"Eliminar Clase"**
3. Confirma la eliminación
4. **Nota**: La clase **Main** no se puede eliminar.

### **¿El sistema funciona offline?**
No, POOGraph requiere conexión a internet para compilar y guardar tu código.

---

## 🆘 Resolución de Problemas

### **Error: "No se pudo conectar con el servidor"**

**Solución:**
1. Verifica que el backend esté corriendo: `http://localhost:8000`
2. Revisa la configuración de CORS en el backend
3. Recarga la página (`F5`)

### **Error: "Compilación falló - compilador no encontrado"**

**Solución:**
1. Verifica que Java JDK o g++ estén instalados en el servidor
2. Contacta a tu profesor o administrador del sistema

### **El diagrama no se actualiza**

**Solución:**
1. Haz clic en el botón **"🔄 Recargar Diagrama"** en la barra superior
2. Guarda el archivo actual (cambia de archivo y vuelve)
3. Recarga la página completa (`F5`)

### **No puedo iniciar sesión**

**Solución:**
1. Verifica que tu usuario y contraseña sean correctos
2. Asegúrate de estar registrado
3. Limpia la caché del navegador (`Ctrl+Shift+Del`)
4. Intenta con otro navegador (Chrome recomendado)

### **El editor está lento**

**Solución:**
1. Cierra otras pestañas del navegador
2. Desactiva extensiones del navegador
3. Reduce el tamaño del diagrama o ocúltalo temporalmente

---

## 📞 Soporte

Si tienes problemas técnicos o preguntas sobre la plataforma:

- **Profesor/Instructor**: Contacta a tu profesor del curso
- **Soporte Técnico**: [Correo del administrador del sistema]
- **Feedback**: Tus comentarios son importantes para mejorar POOGraph

---

## 🎓 ¡Comienza a Aprender!

Ya estás listo para aprovechar al máximo **POOGraph**. Recuerda:

1. ✍️ **Practica regularmente** - La programación se aprende haciendo
2. 💡 **Usa los tooltips** - Son tu tutor personal
3. 🔍 **Experimenta** - No tengas miedo de romper cosas, siempre puedes reiniciar
4. 📊 **Sigue tu progreso** - Observa cómo mejoras con el tiempo
5. 🤝 **Colabora** - Pregunta a tus compañeros y profesor

**¡Buena suerte en tu viaje de aprendizaje de POO! 🚀**

---

*Última actualización: Julio 2026*  
*Versión: 1.0*  
*Universidad Autónoma de Aguascalientes*

