import subprocess
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.files.storage import FileSystemStorage
from .models import *
import os
from .serializers import *
from .utils import actualizar_archivo_java_desde_bd, analizar_codigo_java, generar_codigo_main, generar_plantilla_java, guardar_archivo_fisico, registrar_xapi, procesar_nombre_metodo_java 
from .models import LogActividad # Para los logs de tesis
import re
from rest_framework.exceptions import ValidationError


# --- UTILIDAD: SUBIDA DE ARCHIVOS ---
@api_view(['POST'])
def upload_file(request):
    if 'myFile' not in request.FILES:
        return Response({"error": "No se envió archivo"}, status=400)
    
    archivo = request.FILES['myFile']
    fs = FileSystemStorage(location='archivos/') 
    filename = fs.save(archivo.name, archivo)
    return Response({'data': 'OK', 'filename': filename})

@api_view(['GET'])
def welcome(request):
    return Response("Welcome")

# --- VISTAS UNIFICADAS (ATRIBUTOS) ---
@api_view(['GET', 'POST'])
def gestionar_atributos(request):
    if request.method == 'GET':
        data = Getatributos.objects.all()
        serializer = GetAtributosSerializer(data, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AtributosSerializer(data=request.data)
        if serializer.is_valid():
            nuevo_atributo = serializer.save()
            id_clase = nuevo_atributo.id_clase.pk
            actualizar_archivo_java_desde_bd(id_clase)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
@api_view(['GET'])
def obtenerAtributosClase(request, id):
    if request.method == 'GET':
        data = Atributos.objects.filter(id_clase = id)
        serializer = AtributosSerializer(data, many=True)
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def obtenerFuncionesClase(request, id):
    if request.method == 'GET':
        data = Funciones.objects.filter(id_clase = id)
        serializer = FuncionesSerializer(data, many=True)
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['PUT', 'DELETE'])
def gestionar_atributo_individual(request, id):
    try:
        atributo = Atributos.objects.get(pk=id)
    except Atributos.DoesNotExist:
        return Response(status=404)

    if request.method == 'PUT':
        serializer = AtributosSerializer(atributo, data=request.data, partial=True)
        if serializer.is_valid():
            atributo_actualizado = serializer.save()
            registrar_xapi(
                atributo_actualizado.id_clase.id_proyecto.id_usr.username, 
                "agregó_atributo", 
                f"Atributo '{atributo_actualizado.nombre}' ({atributo_actualizado.tipo}) a la clase '{atributo_actualizado.id_clase.nombre}'"
            )
            actualizar_archivo_java_desde_bd(atributo_actualizado.id_clase.pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        id_clase_padre = atributo.id_clase.pk
        clase = Clase.objects.get(pk=id_clase_padre)
        registrar_xapi(
                clase.id_usr.username, 
                "eliminó_atributo", 
                f"Atributo '{atributo.nombre}' ({atributo.tipo}) a la clase '{atributo.id_clase.nombre}'"
        )
        atributo.delete() 
        actualizar_archivo_java_desde_bd(id_clase_padre)
        
        return Response({"msg": "Atributo eliminado y archivo actualizado"})

# --- VISTAS UNIFICADAS (FUNCIONES) ---
@api_view(['GET', 'POST'])
def gestionar_funciones(request):
    if request.method == 'GET':
        data = Getfunciones.objects.all()
        serializer = GetFuncionesSerializer(data, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        try:
            # Usamos el helper
            if 'nombre' in data:
                data['nombre'] = procesar_nombre_metodo_java(data['nombre'])
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        serializer = FuncionesSerializer(data=data)
        if serializer.is_valid():
            nueva_funcion = serializer.save()
            actualizar_archivo_java_desde_bd(nueva_funcion.id_clase.pk)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PUT', 'DELETE'])
def gestionar_funcion_individual(request, id):
    if request.method == 'PUT':
        try:
            # 1. Buscamos la función que vamos a editar
            funcion_existente = Funciones.objects.get(pk=id)
        except Funciones.DoesNotExist:
            return Response({"error": "Función no encontrada"}, status=404)

        # 2. Copiamos la data entrante
        data = request.data.copy()

        # 3. APLICAMOS LA MISMA LÓGICA DE LIMPIEZA
        try:
            # Solo procesamos si el usuario envió el campo 'nombre' para cambiarlo
            if 'nombre' in data:
                data['nombre'] = procesar_nombre_metodo_java(data['nombre'])
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        # 4. Pasamos la instancia a editar al Serializer
        serializer = FuncionesSerializer(funcion_existente, data=data) # <--- OJO: Pasar instancia
        
        if serializer.is_valid():
            funcion_actualizada = serializer.save()
            
            # 5. IMPORTANTE: Regenerar el archivo Java
            actualizar_archivo_java_desde_bd(funcion_actualizada.id_clase.pk)
            
            return Response(serializer.data)
            
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        # Replica la lógica de Node.js: borrar funciones de una CLASE
        Funciones.objects.filter(id_clase=id).delete()
        actualizar_archivo_java_desde_bd(id)
        return Response({"msg": "Deleted"})

# --- VISTAS UNIFICADAS (HERENCIA) ---
@api_view(['GET', 'DELETE'])
def gestionar_herencia_hijo(request, id):
    """
    GET /herencia/:id -> Trae herencias filtradas por PROYECTO (id es id_proyecto)
    DELETE /herencia/:id -> Borra herencia filtrada por HIJO (id es id_claseHijo)
    """
    if request.method == 'GET':
        data = Herenciaf.objects.filter(id_proyecto=id)
        serializer = HerenciaFSerializer(data, many=True)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        Herencia.objects.filter(id_clasehijo=id).delete()
        return Response({"msg": "Deleted"})

@api_view(['POST'])
def crear_herencia(request):
    serializer = HerenciaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def eliminar_herencia_padre(request, id):
    Herencia.objects.filter(id_clasepadre=id).delete()
    return Response({"msg": "Deleted"})

# --- CLASES Y PROYECTOS (CONSULTAS SIMPLES) ---
@api_view(['GET'])
def get_clases_proyecto(request, id):
    clases = Clase.objects.filter(id_proyecto=id)
    serializer = ClaseSerializer(clases, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_clase_id(request):
    n1 = request.query_params.get('n1') # id_proyecto
    n2 = request.query_params.get('n2') # nombre
    clases = Clase.objects.filter(nombre=n2, id_proyecto=n1).values('id')
    return Response(list(clases))

@api_view(['POST'])
def crear_clase(request):
    datos = request.data
    try:
        # 1. Crear la Clase en BD (Sin código aún)
        proyecto_instancia = Proyecto.objects.get(pk=datos['id_proyecto'])
        nueva_clase = Clase.objects.create(
            nombre=datos['nombre'],
            id_proyecto=proyecto_instancia,
            nivel=datos['nivel'],
            imagen=datos['imagen']
        )
        print(nueva_clase)
        codigo = generar_plantilla_java(nueva_clase.nombre, [], [])
        ruta = guardar_archivo_fisico(datos['id_usuario'], datos['id_proyecto'], nueva_clase.nombre, codigo)
        nueva_clase.path_archivo = ruta
        nueva_clase.save()

        return Response({"msg": "Clase creada", "id": nueva_clase.pk, "path": ruta})
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# --- USUARIOS Y PROYECTOS ---
@api_view(['GET', 'POST'])
def gestionar_usuarios(request):
    if request.method == 'GET':
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_proyectos_usuario(request, id):
    proyectos = Proyecto.objects.filter(id_usr=id)
    serializer = ProyectoSerializer(proyectos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_proyecto_individual(request):
    n1 = request.query_params.get('n1') # id_usr
    n2 = request.query_params.get('n2') # nombre
    proyectos = Proyecto.objects.filter(id_usr=n1, nombre=n2)
    serializer = ProyectoSerializer(proyectos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def crear_proyecto(request):
    serializer = ProyectoSerializer(data=request.data)
    if serializer.is_valid():
        proyecto_nuevo=serializer.save()
        try:
            # 1. Generar código
            codigo_main = generar_codigo_main()
            
            # 2. Guardar archivo físico (Main.java)
            ruta_main = guardar_archivo_fisico(
                usuario_id=proyecto_nuevo.id_usr.pk, # O el campo que uses para usuario
                proyecto_id=proyecto_nuevo.pk,
                nombre_clase="Main",
                codigo_texto=codigo_main
            )
            
            # 3. Guardar registro en la BD de Clases
            # Esto es vital para que aparezca en el diagrama y en la lista de archivos
            Clase.objects.create(
                nombre="Main",
                id_proyecto=proyecto_nuevo, # Pasamos la instancia del proyecto recién creado
                path_archivo=ruta_main,
                codigo_fuente=codigo_main,
                # coordenadas_x = 100, (Opcional: dales una posición fija inicial)
                # coordenadas_y = 100
            )
            
        except Exception as e:
            print(f"Error creando Main automático: {e}")
            # No retornamos error al front para no bloquear la creación del proyecto, 
            # pero lo dejamos en consola.

        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# --- STORED PROCEDURES ---
@api_view(['GET'])
def get_atributos_heredados(request, id):
    with connection.cursor() as cursor:
        cursor.callproc('getAtributosHeredados', [id])
        results = cursor.fetchall()
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            json_result = [dict(zip(columns, row)) for row in results]
            return Response(json_result)
        return Response([])

# --- TESIS: PARSER & LOGS ---
@api_view(['POST'])
def parsear_codigo(request):
    codigo = request.data.get('codigo', '')
    usuario_id = request.data.get('usuario', 'Desconocido')
    
    if not codigo:
        return Response({"error": "No se envió código"}, status=400)

    # 1. Analizar con javalang
    resultado = analizar_codigo_java(codigo)
    
    # 2. Guardar Log
    tiene_errores = len(resultado['errores']) > 0
    accion = "intento_diagramar_error" if tiene_errores else "intento_diagramar_exito"
    
    LogActividad.objects.create(
        usuario=usuario_id,
        accion=accion,
        detalle=f"Errores: {resultado['errores']}" if tiene_errores else "Sintaxis correcta"
    )

    return Response(resultado)

@api_view(['POST'])
def registrar_log(request):
    serializer = LogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "Log guardado"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def crear_clase_con_codigo(request):
    """
    Recibe: {
        "nombre": "Perro",
        "id_proyecto": 1,
        "atributos": [...],
        "metodos": [...]
    }
    Acción: Crea registro en BD, genera código Java y guarda el archivo físico.
    """
    datos = request.data
    nombre = datos.get('nombre')
    id_proyecto = datos.get('id_proyecto')
    atributos = datos.get('atributos', []) # Lista vacía si no envían nada
    metodos = datos.get('metodos', [])

    # 1. Validaciones básicas
    if not nombre or not id_proyecto:
        return Response({"error": "Faltan datos obligatorios"}, status=400)

    try:
        # 2. Generamos el String del código Java
        codigo_fuente = generar_plantilla_java(nombre, atributos, metodos)

        # 3. Guardamos el archivo físico en el servidor
        # (Asumimos usuario_id = 1 temporalmente o extráelo del request si tienes auth)
        ruta_archivo = guardar_archivo_fisico(
            usuario_id=1, 
            proyecto_id=id_proyecto, 
            nombre_clase=nombre, 
            codigo_texto=codigo_fuente
        )

        # 4. Guardamos en Base de Datos (Modelo Clase)
        # Nota: Ajusta los campos según tu modelo real
        nueva_clase = Clase.objects.create(
            nombre=nombre,
            id_proyecto=id_proyecto,
            path_archivo=ruta_archivo,  # Guardamos la ruta del archivo físico
            codigo_fuente=codigo_fuente, # Opcional: si quieres respaldo en texto en BD
            # ... otros campos por defecto ...
        )

        # 5. Guardamos los atributos/métodos en sus tablas relacionales (si las usas)
        # Esto es para que el diagrama se dibuje bien al recargar
        # ... lógica para insertar en tabla 'atributo' y 'metodo' ...

        return Response({
            "msg": "Clase creada exitosamente",
            "id": nueva_clase.pk,
            "path": ruta_archivo,
            "codigo": codigo_fuente
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(['GET', 'DELETE', 'PATCH'])
def gestionar_clase_individual(request, id):
    try:
        clase = Clase.objects.get(pk=id)
    except Clase.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        clases = Clase.objects.filter(id=id)
        serializer = Clase(clases, many=True)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        try:
            # --- PASO 1: GESTIONAR HERENCIA (CRÍTICO) ---
            
            # A. Caso: La clase que borramos es HIJA
            # Simplemente borramos el registro de la tabla Herencia.
            Herencia.objects.filter(id_clasehijo=id).delete()

            # B. Caso: La clase que borramos es PADRE
            # Aquí es más complejo: Los hijos quedan "huérfanos". 
            # Debemos borrar la relación Y regenerar el archivo del hijo para quitar el 'extends'.
            relaciones_donde_soy_padre = Herencia.objects.filter(id_clasepadre=id)
            for relacion in relaciones_donde_soy_padre:
                # 1. Guardamos el ID del hijo antes de borrar la relación
                id_hijo_huerrfano = relacion.id_clasehijo.pk
                # 2. Borramos el registro de herencia
                relacion.delete()
                
                # 3. REGENERAMOS el archivo del hijo inmediatamente
                actualizar_archivo_java_desde_bd(id_hijo_huerrfano)


            Atributos.objects.filter(id_clase=id).delete()
            Funciones.objects.filter(id_clase=id).delete()


            # --- PASO 3: BORRAR ARCHIVO FÍSICO ---
            if clase.path_archivo:
                full_path = os.path.join(settings.BASE_DIR, clase.path_archivo)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print(f"No se pudo borrar el archivo físico: {e}")


            # --- PASO 4: BORRAR LA CLASE FINALMENTE ---
            clase.delete()
            
            return Response({"msg": "Clase eliminada y todas sus referencias limpiadas correctamente"})
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def obtener_codigo_clase(request, id):
    """
    Recibe el ID de la clase.
    Busca su 'path_archivo', lee el contenido del disco y lo devuelve.
    """
    try:
        # 1. Buscamos la clase en la BD
        clase = Clase.objects.get(pk=id)
        
        # 2. Verificamos si tiene ruta asignada
        if not clase.path_archivo:
            return Response({"error": "Esta clase no tiene un archivo asociado."}, status=404)
            
        # 3. Construimos la ruta absoluta
        ruta_absoluta = os.path.join(settings.BASE_DIR, clase.path_archivo)
        
        # 4. Verificamos que el archivo exista físicamente
        if not os.path.exists(ruta_absoluta):
            return Response({"error": "El archivo físico no se encuentra en el servidor."}, status=404)
            
        # 5. Leemos el contenido
        with open(ruta_absoluta, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            
        return Response({"codigo": contenido})

    except Clase.DoesNotExist:
        return Response({"error": "Clase no encontrada"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

@api_view(['GET'])
def listar_archivos_proyecto(request, proyecto_id):
    """
    Lista todos los archivos .java físicos que existen en la carpeta del proyecto.
    """
    try:
        # 1. Recuperamos el proyecto para saber el ID del usuario
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        
        # 2. Construimos la ruta: codigos_fuente/usuario_X/proyecto_Y
        # Ajusta 'id_usr' si en tu modelo es un objeto o un ID directo
        id_usuario = proyecto.id_usr.id if hasattr(proyecto.id_usr, 'id') else proyecto.id_usr
        
        ruta_relativa = os.path.join('codigos_fuente', f'usuario_{id_usuario}', f'proyecto_{proyecto.id}')
        ruta_absoluta = os.path.join(settings.BASE_DIR, ruta_relativa)

        archivos = []
        
        if os.path.exists(ruta_absoluta):
            # 3. Listamos lo que hay en la carpeta
            for nombre_archivo in os.listdir(ruta_absoluta):
                if nombre_archivo.endswith(".java"):
                    archivos.append({
                        "nombre": nombre_archivo,
                        "ruta_relativa": os.path.join(ruta_relativa, nombre_archivo),
                        "es_main": nombre_archivo == "Main.java" # Flag útil para el front
                    })
        
        return Response(archivos)

    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['POST'])
def leer_archivo_fisico(request):
    ruta = request.data.get('ruta') # "codigos_fuente/usuario_1/..."
    ruta_abs = os.path.join(settings.BASE_DIR, ruta)
    try:
        with open(ruta_abs, 'r', encoding='utf-8') as f:
            return Response({"codigo": f.read()})
    except Exception as e:
        return Response({"error": "No se pudo leer"}, status=404)


@api_view(['POST'])
def compilar_y_ejecutar_proyecto(request):
    """
    Recibe: { "id_proyecto": 1 }
    1. Compila TODOS los archivos .java en la carpeta del proyecto.
    2. Ejecuta la clase 'Main'.
    """
    id_proyecto = request.data.get('id_proyecto')
    entradas_usuario = request.data.get('entradas')
    try:
        # 1. Obtener la ruta de la carpeta del proyecto
        proyecto = Proyecto.objects.get(pk=id_proyecto)
        
        # Ajusta esto si tu id_usr es un objeto o un entero, igual que hicimos antes
        uid = proyecto.id_usr.id if hasattr(proyecto.id_usr, 'id') else proyecto.id_usr
        
        ruta_relativa = os.path.join('codigos_fuente', f'usuario_{uid}', f'proyecto_{proyecto.id}')
        ruta_absoluta = os.path.join(settings.BASE_DIR, ruta_relativa)

        if not os.path.exists(ruta_absoluta):
            return Response({"exito": False, "mensaje": "Error: La carpeta del proyecto no existe."}, status=404)

        # 2. Identificar todos los archivos .java para compilarlos juntos
        # Esto es vital para que Main.java reconozca a Perro.java, etc.
        archivos_java = [f for f in os.listdir(ruta_absoluta) if f.endswith('.java')]
        
        if not archivos_java:
            return Response({"exito": False, "mensaje": "No hay archivos .java para compilar."})

        # --- FASE DE COMPILACIÓN ---
        # Comando: javac -encoding utf8 Main.java Perro.java Gato.java ...
        comando_compile = ['javac', '-encoding', 'utf-8'] + archivos_java

        if entradas_usuario:
            if not entradas_usuario.endswith('\n'):
                entradas_usuario += '\n'
        
        proceso_compile = subprocess.run(
            comando_compile,
            cwd=ruta_absoluta,     # Ejecutar DENTRO de la carpeta
            capture_output=True,   # Capturar lo que salga en consola
            text=True,             # Que lo devuelva como texto, no bytes
            timeout=10
        )

        # Si el código de retorno no es 0, hubo error de sintaxis
        if proceso_compile.returncode != 0:
            return Response({
                "exito": False, 
                "mensaje": "❌ Error de Compilación:\n" + proceso_compile.stderr
            })

        # --- FASE DE EJECUCIÓN ---
        # Verificamos si existe Main.class (o Main.java en la lista)
        if "Main.java" not in archivos_java:
             return Response({"exito": False, "mensaje": "⚠️ Compilación exitosa, pero no se encontró 'Main.java' para ejecutar."})

        try:
            # Comando: java -cp . Main  (-cp . es ClassPath actual)
            proceso_run = subprocess.run(
                ['java', '-cp', '.', 'Main'], 
                cwd=ruta_absoluta,
                capture_output=True, 
                input=entradas_usuario,
                text=True,
                timeout=10
            )
            
            # Unimos stdout (salida normal) y stderr (errores en ejecución)
            salida = proceso_run.stdout
            if proceso_run.stderr:
                salida += "\n⚠️ Errores durante la ejecución:\n" + proceso_run.stderr

            return Response({"exito": True, "mensaje": salida})

        except subprocess.TimeoutExpired:
            return Response({
                "exito": False, 
                "mensaje": "⏱️ Error: El programa tardó demasiado en responder (Timeout 5s).\nPosible bucle infinito o espera de input no soportada."
            })

    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": "Error interno del servidor: " + str(e)}, status=500)

@api_view(['POST'])
def guardar_archivo_cambios(request):
    """
    Recibe: { "ruta_relativa": "codigos_fuente/...", "codigo": "public class..." }
    Acción: Sobrescribe el archivo en el disco.
    """
    ruta_relativa = request.data.get('ruta_relativa')
    nuevo_codigo = request.data.get('codigo')

    if not ruta_relativa or nuevo_codigo is None:
        return Response({"error": "Faltan datos"}, status=400)

    try:
        ruta_absoluta = os.path.join(settings.BASE_DIR, ruta_relativa)
        
        # Escribimos el archivo (modo 'w' sobrescribe todo)
        with open(ruta_absoluta, 'w', encoding='utf-8') as f:
            f.write(nuevo_codigo)
            
        return Response({"msg": "Guardado exitoso"})
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)