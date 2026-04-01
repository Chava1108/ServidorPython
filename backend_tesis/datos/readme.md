Dataset de Logs de Actividad - Proyecto POOGRAPH
Este repositorio contiene el archivo log_actividad.csv, el cual registra las interacciones de los usuarios dentro de la herramienta educativa POOGRAPH. Este dataset es fundamental para el análisis de comportamiento y la implementación de modelos de Machine Learning enfocados en la educación.

Nota sobre los Datos Sintéticos
Es importante destacar que los datos contenidos en este archivo son datos sintéticos. Fueron generados algorítmicamente mediante un script de Python para simular el comportamiento de 5 estudiantes durante un periodo de una semana de uso intensivo.

Propósito de estos datos:

Validar la arquitectura de la base de datos MariaDB.

Probar el flujo de transformación de datos mediante dbt (Data Build Tool).

Entrenar prototipos iniciales de modelos de MLOps antes de la fase de pruebas reales programada para agosto.

Estructura del Dataset
El archivo sigue una estructura basada en el estándar xAPI (Actor-Verbo-Objeto), permitiendo una granularidad alta en el seguimiento del aprendizaje de Programación Orientada a Objetos.

Columna,Descripción,Ejemplo
id,Identificador único del registro de log.,152
usuario_id,ID del estudiante (anonimizado para fines de investigación).,1
proyecto_id,Identificador del proyecto de programación (Java/C++).,10
verbo,La acción realizada por el estudiante.,"compilo, heredo"
objeto,El componente del diagrama o código afectado.,"clase, metodo"
resultado,Estado de la acción (exitoso o error de sintaxis).,error_sintaxis
timestamp,Marca de tiempo del evento (Zona horaria: UTC-6).,2026-03-30 11:00:00

Diccionario de Verbos (Contexto POOGRAPH)
Para interpretar correctamente el archivo, se definen las siguientes acciones clave:

creo: El alumno generó una nueva clase o atributo desde la interfaz gráfica.

modifico: Se realizó un cambio en la estructura o el código mediante la inyección quirúrgica.

heredo: Se estableció una relación de herencia entre una clase padre e hija.

compilo: El alumno intentó generar el archivo ejecutable (.exe) desde el Main.

Contexto Académico
Este trabajo forma parte de la investigación de tesis para la Maestría en Informática y Tecnologías Computacionales (MITC) en la Universidad Autónoma de Aguascalientes.
