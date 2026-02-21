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
from .utils import *
from .models import LogActividad # Para los logs de tesis
import re
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .compile import compilar_cpp, compilar_java

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
            id_clase = nuevo_atributo.id_clase
            registrar_xapi(
                id_clase.id_proyecto.id_usr.id, 
                "agregó_atributo", 
                f"Atributo '{nuevo_atributo.nombre}' ({nuevo_atributo.tipo}) a la clase '{nuevo_atributo.id_clase.nombre}'"
            )
            actualizar_archivo_java_desde_bd(id_clase.id)
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
                atributo_actualizado.id_clase.id_proyecto.id_usr.id, 
                "modificó_atributo", 
                f"Atributo '{atributo_actualizado.nombre}' ({atributo_actualizado.tipo}) a la clase '{atributo_actualizado.id_clase.nombre}'"
            )
            actualizar_archivo_java_desde_bd(atributo_actualizado.id_clase.pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        id_clase_padre = atributo.id_clase.pk
        clase = Clase.objects.get(pk=id_clase_padre)
        registrar_xapi(
                clase.id_proyecto.id_usr.id, 
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
            registrar_xapi(
                nueva_funcion.id_clase.id_proyecto.id, 
                "agregó_función", 
                f"Funcion '{nueva_funcion.nombre}' ({nueva_funcion.tipo}) a la clase '{nueva_funcion.id_clase.nombre}'"
            )
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
            registrar_xapi(
                funcion_actualizada.id_clase.id_proyecto.id_usr.id, 
                "modificó_función", 
                f"Funcion '{funcion_actualizada.nombre}' ({funcion_actualizada.tipo}) a la clase '{funcion_actualizada.id_clase.nombre}'"
            )
            actualizar_archivo_java_desde_bd(funcion_actualizada.id_clase.pk)
            
            return Response(serializer.data)
            
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        funcion_existente = Funciones.objects.get(pk=id)
        registrar_xapi(
            funcion_existente.id_clase.id_proyecto.id_usr.id, 
            "eliminó_función", 
            f"Funcion '{funcion_existente.nombre}' ({funcion_existente.tipo}) a la clase '{funcion_existente.id_clase.nombre}'"
        )
        funcion_existente.delete()
        
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
    print(request.data)
    if serializer.is_valid():
        herencia = serializer.save()
        id_del_usuario = herencia.id_claseHijo.id_proyecto.id_usr.id
        registrar_xapi(
            id_del_usuario, 
            "creó_herencia", 
            f"Hija: {herencia.id_claseHijo.nombre} extiende de Padre: {herencia.id_clasePadre.nombre}"
        )
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
        
        print(datos) 
        proyecto_instancia = Proyecto.objects.get(pk=datos['id_proyecto'])
        nueva_clase = Clase.objects.create(
            nombre=datos['nombre'],
            id_proyecto=proyecto_instancia,
            nivel=datos['nivel'],
            imagen=datos['imagen'],

        )
        print(nueva_clase)
        codigo = generar_plantilla_java(nueva_clase.nombre, [], []) if proyecto_instancia.lenguaje == 'java' else generar_plantilla_cpp(nueva_clase.nombre, [], [])
        ruta = guardar_archivo_fisico(datos['id_usuario'], datos['id_proyecto'], nueva_clase.nombre, codigo, proyecto_instancia.lenguaje)
        nueva_clase.path_archivo = ruta
        nueva_clase.save()
        registrar_xapi(
            datos['id_usuario'], 
            "creó_clase", 
            f"Clase {nueva_clase.nombre}"
        )
        return Response({"msg": "Clase creada", "id": nueva_clase.pk, "path": ruta})
        
    except Exception as e:
        print(str(e))
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
    print(f"n1 = {n1} n2  = {n2}")
    proyectos = Proyecto.objects.filter(id_usr=n1, nombre=n2)
    serializer = ProyectoSerializer(proyectos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def crear_proyecto(request):
    serializer = ProyectoSerializer(data=request.data)
    if serializer.is_valid():
        proyecto_nuevo=serializer.save()
        registrar_xapi(
            proyecto_nuevo.id_usr.pk, 
            "creó_proyecto", 
            f"Proyecto '{proyecto_nuevo.nombre}'"
        )
        try:
            # 1. Generar código
            codigo_main = generar_codigo_main(proyecto_nuevo.lenguaje)
            
            # 2. Guardar archivo físico (Main.java)
            ruta_main = guardar_archivo_fisico(
                usuario_id=proyecto_nuevo.id_usr.pk, # O el campo que uses para usuario
                proyecto_id=proyecto_nuevo.pk,
                nombre_clase="Main",
                codigo_texto=codigo_main,
                lenguaje=proyecto_nuevo.lenguaje
            )
            

            Clase.objects.create(
                nombre="Main",
                id_proyecto=proyecto_nuevo, # Pasamos la instancia del proyecto recién creado
                path_archivo=ruta_main,

            )
            
        except Exception as e:
            print(f"Error creando Main automático: {e}")


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
            Herencia.objects.filter(id_claseHijo=id).delete()

            # B. Caso: La clase que borramos es PADRE
            # Aquí es más complejo: Los hijos quedan "huérfanos". 
            # Debemos borrar la relación Y regenerar el archivo del hijo para quitar el 'extends'.
            relaciones_donde_soy_padre = Herencia.objects.filter(id_clasePadre=id)
            for relacion in relaciones_donde_soy_padre:
                # 1. Guardamos el ID del hijo antes de borrar la relación
                id_hijo_huerrfano = relacion.id_claseHijo.pk
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
    Lista los archivos .java O .cpp físicos en la carpeta, según el lenguaje del proyecto.
    """
    try:
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        
        id_usuario = proyecto.id_usr.id if hasattr(proyecto.id_usr, 'id') else proyecto.id_usr
        
        ruta_relativa = os.path.join('codigos_fuente', f'usuario_{id_usuario}', f'proyecto_{proyecto.id}')
        ruta_absoluta = os.path.join(settings.BASE_DIR, ruta_relativa)

        archivos = []
        
        es_cpp = proyecto.lenguaje == 'cpp'
        
        extension_buscada = ".cpp" if es_cpp else ".java"
        archivo_main_esperado = "Main.cpp" if es_cpp else "Main.java"

        if os.path.exists(ruta_absoluta):
            for nombre_archivo in os.listdir(ruta_absoluta):
                if nombre_archivo.endswith(extension_buscada):
                    archivos.append({
                        "nombre": nombre_archivo,
                        "ruta_relativa": os.path.join(ruta_relativa, nombre_archivo),
                        "es_main": nombre_archivo == archivo_main_esperado, 
                        "lenguaje": proyecto.lenguaje 
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
    id_proyecto = request.data.get('id_proyecto')
    entradas_usuario = request.data.get('entradas', "")
    
    if entradas_usuario and not entradas_usuario.endswith('\n'):
        entradas_usuario += '\n'

    try:
        # 1. Obtener datos
        proyecto = Proyecto.objects.get(pk=id_proyecto)
        uid = proyecto.id_usr.id if hasattr(proyecto.id_usr, 'id') else proyecto.id_usr
        
        ruta_relativa = os.path.join('codigos_fuente', f'usuario_{uid}', f'proyecto_{proyecto.id}')
        ruta_absoluta = os.path.join(settings.BASE_DIR, ruta_relativa)

        if not os.path.exists(ruta_absoluta):
            return Response({"exito": False, "mensaje": "Error: Carpeta no encontrada."}, status=404)

        # 2. DECISIÓN BASADA EN BD (Mucho más robusto)
        resultado = {}
        
        # Usamos el campo nuevo 'lenguaje'
        if proyecto.lenguaje == 'cpp':
            # Solo buscamos archivos cpp
            archivos_cpp = [f for f in os.listdir(ruta_absoluta) if f.endswith('.cpp')]
            if not archivos_cpp:
                return Response({"exito": False, "mensaje": "El proyecto es C++ pero no hay archivos .cpp"})
                
            resultado = compilar_cpp(ruta_absoluta, archivos_cpp, entradas_usuario)

        elif proyecto.lenguaje == 'java':
            # Solo buscamos archivos java
            archivos_java = [f for f in os.listdir(ruta_absoluta) if f.endswith('.java')]
            if not archivos_java:
                return Response({"exito": False, "mensaje": "El proyecto es Java pero no hay archivos .java"})
                
            resultado = compilar_java(ruta_absoluta, archivos_java, entradas_usuario)
            
        else:
            return Response({"exito": False, "mensaje": f"Lenguaje '{proyecto.lenguaje}' no soportado aún."})

        # 3. LOGS (Igual que antes)
        if resultado['exito']:
            registrar_xapi(uid, f"compiló_{proyecto.lenguaje}", f"Éxito en proyecto {proyecto.id}")
        else:
            tipo = resultado.get('tipo_error', 'general')
            registrar_xapi(uid, f"error_{tipo}_{proyecto.lenguaje}", f"Fallo en proyecto {proyecto.id}")

        return Response(resultado)

    except Proyecto.DoesNotExist:
        return Response({"error": "Proyecto no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": "Error interno: " + str(e)}, status=500)

@api_view(['POST'])
def guardar_archivo_cambios(request):
    """
    Recibe: { "ruta_relativa": "codigos_fuente/...", "codigo": "public class..." }
    Acción: Sobrescribe el archivo en el disco.
    """
    ruta_relativa = request.data.get('ruta_relativa')
    nuevo_codigo = request.data.get('codigo')
    id_proyecto = request.data.get('id_proyecto')
    if not ruta_relativa or nuevo_codigo is None:
        return Response({"error": "Faltan datos"}, status=400)
    
    try:
        proyecto = Proyecto.objects.get(pk=id_proyecto)
        ruta_absoluta = os.path.join(settings.BASE_DIR, ruta_relativa)
        registrar_xapi(
            proyecto.id_usr.id if hasattr(proyecto.id_usr, 'id') else proyecto.id_usr, 
            "guardó_código", 
            f"Archivo: {ruta_relativa} (Proyecto: {proyecto.nombre})"
        )
        # Escribimos el archivo (modo 'w' sobrescribe todo)
        with open(ruta_absoluta, 'w', encoding='utf-8') as f:
            f.write(nuevo_codigo)
            
        return Response({"msg": "Guardado exitoso"})
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['POST'])
def login_view(request):
    # 1. Obtener datos del JSON que envía Angular
    username = request.data.get('username')
    password = request.data.get('password')

    # 2. Validar que vengan los datos
    if not username or not password:
        return Response(
            {'error': 'Faltan credenciales'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. Autenticación Mágica de Django
    # Esto revisa el hash de la contraseña de forma segura.
    user = authenticate(request, username=username, password=password)

    if user is not None:
        if user.is_active:
            # --- ZONA DE LOGS PARA TU TESIS ---
            # Registramos que el alumno entró exitosamente
            token, created = Token.objects.get_or_create(user=user)
            registrar_xapi(user.id, "inició_sesión", "Acceso desde Login Web")
            
            # 4. Respuesta Exitosa
            # Devolvemos solo lo necesario para el frontend
            return Response({
                'id': user.id,
                'username': user.username,
                'token': token.key,
                'mensaje': 'Login exitoso'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Usuario desactivado'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        # 5. Fallo de autenticación
        # Registramos el intento fallido (Opcional, pero bueno para seguridad)
        print(f"Intento fallido de login para: {username}")
        return Response(
            {'error': 'Credenciales incorrectas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Solo usuarios logueados pueden llamar a esto
def logout_view(request):
    # Obtenemos la razón del logout (Manual o Inactividad)
    motivo = request.data.get('motivo', 'manual')
    
    # 1. LOG PARA TU TESIS
    verbo = "cerró_sesión_inactividad" if motivo == 'timeout' else "cerró_sesión_manual"
    detalle = "El sistema cerró la sesión por 10 min sin actividad" if motivo == 'timeout' else "El usuario dio click en salir"
    
    registrar_xapi(request.user.id, verbo, detalle)

    # 2. Respuesta
    return Response({'mensaje': 'Sesión cerrada y registrada'}, status=200)