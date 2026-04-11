from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from .models import *
import os
from .serializers import *
from .utils import *
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .compile import compilar_cpp, compilar_java
from django.utils import timezone
from django.db import transaction

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
        datos = request.data
        id_clase = datos.get('id_clase')
        nombre = datos.get('nombre', '')
        tipo = datos.get('tipo', '')
        nivel = datos.get('nivel', 'private')
        try:
            clase_obj = Clase.objects.get(pk=id_clase)
            proyecto = clase_obj.id_proyecto
            registrar_xapi(
                proyecto.id_usr.id, 
                "agregó_atributo", 
                f"Atributo '{nombre}' ({tipo}) a la clase '{clase_obj.nombre}'"
            )
            nuevo_snippet = f"{nivel} {tipo} {nombre};"
            inyectar_elemento_en_codigo(
                ruta_archivo=clase_obj.path_archivo,
                nuevo_contenido=nuevo_snippet,
                lenguaje=proyecto.lenguaje,
                es_metodo=False
            )
            return Response({"msg": "Atributo agregado", "nombre": nombre, "tipo": tipo}, status=201)
        except Clase.DoesNotExist:
            return Response({"error": "Clase no encontrada"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@api_view(['PUT', 'DELETE'])
def gestionar_atributo_individual(request, id):
    # Ya no se persisten atributos en BD. La edición del código se hace desde Monaco.
    # Solo se registra la actividad xAPI.
    if request.method == 'PUT':
        datos = request.data
        nombre = datos.get('nombre', '')
        tipo = datos.get('tipo', '')
        id_clase = datos.get('id_clase')
        try:
            clase_obj = Clase.objects.get(pk=id_clase) if id_clase else None
            if clase_obj:
                registrar_xapi(
                    clase_obj.id_proyecto.id_usr.id, 
                    "modificó_atributo", 
                    f"Atributo '{nombre}' ({tipo}) en clase '{clase_obj.nombre}'"
                )
        except Clase.DoesNotExist:
            pass
        return Response({"msg": "Atributo modificado", "nombre": nombre})

    elif request.method == 'DELETE':
        try:
            atributo = Atributos.objects.get(pk=id)
            registrar_xapi(
                atributo.id_clase.id_proyecto.id_usr.id, 
                "eliminó_atributo", 
                f"Atributo '{atributo.nombre}' ({atributo.tipo}) de clase '{atributo.id_clase.nombre}'"
            )
            atributo.delete()  # Limpia datos legacy si existen
        except Atributos.DoesNotExist:
            registrar_xapi(0, "eliminó_atributo", f"Atributo eliminado (ID: {id})")
        return Response({"msg": "Atributo eliminado"})

# --- VISTAS UNIFICADAS (FUNCIONES) ---
@api_view(['GET', 'POST'])
def gestionar_funciones(request):
    if request.method == 'GET':
        data = Getfunciones.objects.all()
        serializer = GetFuncionesSerializer(data, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        datos = request.data.copy()
        nombre_nuevo = datos.get('nombre', '')
        tipo = datos.get('tipo', '')
        id_clase = datos.get('id_clase')
        es_metodo = datos.get('es_metodo')
        nivel = datos.get('nivel', 'public')

        try:
            if nombre_nuevo:
                nombre_nuevo = procesar_nombre_metodo_java(nombre_nuevo)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        try:
            clase_obj = Clase.objects.get(pk=id_clase)
            proyecto = clase_obj.id_proyecto

            registrar_xapi(
                proyecto.id_usr.id, 
                "agregó_función", 
                f"Funcion '{nombre_nuevo}' ({tipo}) a la clase '{clase_obj.nombre}'"
            )

            ruta_archivo = clase_obj.path_archivo
            if es_metodo:
                nuevo_snippet = f"{tipo} {nombre_nuevo} {{\n\n    }}"
            else:
                nuevo_snippet = f"{tipo} {nombre_nuevo};"

            inyectar_elemento_en_codigo(
                ruta_archivo=ruta_archivo,
                nuevo_contenido=nuevo_snippet,
                lenguaje=proyecto.lenguaje,
                es_metodo=es_metodo
            )

            return Response({"msg": "Función agregada", "nombre": nombre_nuevo, "tipo": tipo}, status=201)
        except Clase.DoesNotExist:
            return Response({"error": "Clase no encontrada"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    


@api_view(['PUT', 'DELETE'])
def gestionar_funcion_individual(request, id):
    # Ya no se persisten funciones en BD. La edición del código se hace desde Monaco.
    # Solo se registra la actividad xAPI.
    if request.method == 'PUT':
        datos = request.data.copy()
        nombre = datos.get('nombre', '')
        tipo = datos.get('tipo', '')
        id_clase = datos.get('id_clase')

        try:
            if nombre:
                nombre = procesar_nombre_metodo_java(nombre)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        try:
            clase_obj = Clase.objects.get(pk=id_clase) if id_clase else None
            if clase_obj:
                registrar_xapi(
                    clase_obj.id_proyecto.id_usr.id, 
                    "modificó_función", 
                    f"Funcion '{nombre}' ({tipo}) en clase '{clase_obj.nombre}'"
                )
        except Clase.DoesNotExist:
            pass
        return Response({"msg": "Función modificada", "nombre": nombre})

    elif request.method == 'DELETE':
        try:
            funcion = Funciones.objects.get(pk=id)
            registrar_xapi(
                funcion.id_clase.id_proyecto.id_usr.id, 
                "eliminó_función", 
                f"Funcion '{funcion.nombre}' ({funcion.tipo}) de clase '{funcion.id_clase.nombre}'"
            )
            funcion.delete()  # Limpia datos legacy si existen
        except Funciones.DoesNotExist:
            registrar_xapi(0, "eliminó_función", f"Función eliminada (ID: {id})")
        return Response({"msg": "Función eliminada"})

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
        

        proyecto_instancia = Proyecto.objects.get(pk=datos['id_proyecto'])
        nueva_clase = Clase.objects.create(
            nombre=datos['nombre'],
            id_proyecto=proyecto_instancia,
            nivel=datos['nivel'],
            imagen=datos['imagen'],

        )
        nombre_ext = "cpp" if proyecto_instancia.lenguaje  == 'cpp' else "java"
        codigo = generar_plantilla_java(nueva_clase.nombre, [], []) if proyecto_instancia.lenguaje == 'java' else generar_plantilla_cpp(nueva_clase.nombre, [], [])
        ruta = guardar_archivo_fisico(datos['id_usuario'], datos['id_proyecto'], nueva_clase.nombre, codigo, proyecto_instancia.lenguaje)
        nueva_clase.path_archivo = ruta
        nueva_clase.save()
        actualizar_codigo_main(datos['id_usuario'],datos['id_proyecto'], datos['nombre'], proyecto_instancia.lenguaje)
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
            actualizar_codigo_main(proyecto_nuevo.id_usr.pk,proyecto_nuevo.id, "", proyecto_nuevo.lenguaje)
            ruta_relativa_carpeta = os.path.join('codigos_fuente', f'usuario_{proyecto_nuevo.id_usr.pk}', f'proyecto_{proyecto_nuevo.id}')
            ruta_absoluta_carpeta = os.path.join(settings.BASE_DIR, ruta_relativa_carpeta)
            
            extension = '.cpp' if proyecto_nuevo.lenguaje == 'cpp' else '.java'
            nombre_archivo = f"Main{extension}"
            ruta_absoluta_archivo = os.path.join(ruta_absoluta_carpeta, nombre_archivo)

            Clase.objects.create(
                nombre="Main",
                id_proyecto=proyecto_nuevo, # Pasamos la instancia del proyecto recién creado
                path_archivo=ruta_absoluta_archivo,

            )
            
        except Exception as e:
            print(f"Error creando Main automático: {e}")


        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'DELETE'])
def gestionar_clase_individual(request, id):
    try:
        clase = Clase.objects.get(pk=id)
    except Clase.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = ClaseSerializer(clase)
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
            proyecto_instancia = Proyecto.objects.get(pk=clase.id_proyecto)
            eliminar_vinculo_main(clase.id, clase.id_proyecto, clase.nombre, proyecto_instancia.lenguaje)
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


@api_view(['POST'])
def registrar_tooltip(request):
    """
    Registra cuando un estudiante consulta un tooltip o intenta pegar código.
    Payload: { id_usuario, palabra, lenguaje }
    """
    id_usuario = request.data.get('id_usuario')
    palabra = request.data.get('palabra', '')
    lenguaje = request.data.get('lenguaje', '')

    if not id_usuario or not palabra:
        return Response({"error": "Faltan datos"}, status=400)

    if palabra == 'INTENTO_PEGAR':
        verbo = "intentó_pegar_código"
        detalle = f"Intento de pegar código en editor (Lenguaje: {lenguaje})"
    else:
        verbo = "consultó_tooltip"
        detalle = f"Palabra: '{palabra}' (Lenguaje: {lenguaje})"

    registrar_xapi(id_usuario, verbo, detalle)
    return Response({"msg": "Evento registrado"}, status=200)


# ============================================================
# --- VISTAS DE EXÁMENES ---
# ============================================================

@api_view(['POST'])
def crear_examen(request):
    """
    Crea un examen completo con preguntas y opciones en una sola petición.
    Payload: { titulo, fecha_disponible, duracion_minutos, creado_por,
               preguntas: [ { texto, orden, opciones: [ { texto, letra, es_correcta } ] } ] }
    """
    datos = request.data
    try:
        with transaction.atomic():
            creador = Usuario.objects.get(pk=datos['creado_por'])
            examen = Examen.objects.create(
                titulo=datos['titulo'],
                creado_por=creador,
                fecha_disponible=datos['fecha_disponible'],
                duracion_minutos=datos.get('duracion_minutos', 30),
            )

            for p_data in datos.get('preguntas', []):
                pregunta = Pregunta.objects.create(
                    examen=examen,
                    texto=p_data['texto'],
                    orden=p_data.get('orden', 0),
                )
                for op_data in p_data.get('opciones', []):
                    Opcion.objects.create(
                        pregunta=pregunta,
                        texto=op_data['texto'],
                        letra=op_data['letra'],
                        es_correcta=op_data.get('es_correcta', False),
                    )

            registrar_xapi(
                creador.id,
                "creó_examen",
                f"Examen '{examen.titulo}' con {len(datos.get('preguntas', []))} preguntas. Disponible: {examen.fecha_disponible}"
            )

        serializer = ExamenSerializer(examen)
        return Response(serializer.data, status=201)

    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def listar_examenes(request):
    """Lista todos los exámenes activos."""
    examenes = Examen.objects.filter(activo=True).order_by('-fecha_creacion')
    serializer = ExamenListSerializer(examenes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def listar_examenes_disponibles(request, id_estudiante):
    """
    Lista exámenes cuya fecha_disponible ya pasó y que el estudiante NO ha completado.
    """
    ahora = timezone.now()
    examenes_completados = IntentoExamen.objects.filter(
        estudiante_id=id_estudiante, completado=True
    ).values_list('examen_id', flat=True)

    examenes = Examen.objects.filter(
        activo=True,
        fecha_disponible__lte=ahora
    ).exclude(id__in=examenes_completados).order_by('-fecha_disponible')

    serializer = ExamenListSerializer(examenes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def obtener_examen_estudiante(request, id_examen):
    """
    Devuelve el examen con preguntas y opciones, SIN marcar cuál es correcta.
    Para uso del estudiante al responder.
    """
    try:
        examen = Examen.objects.get(pk=id_examen, activo=True)
    except Examen.DoesNotExist:
        return Response({"error": "Examen no encontrado"}, status=404)

    data = {
        "id": examen.id,
        "titulo": examen.titulo,
        "duracion_minutos": examen.duracion_minutos,
        "fecha_disponible": examen.fecha_disponible,
        "preguntas": []
    }

    for pregunta in examen.preguntas.all().order_by('orden'):
        p_data = {
            "id": pregunta.id,
            "texto": pregunta.texto,
            "orden": pregunta.orden,
            "opciones": []
        }
        for opcion in pregunta.opciones.all():
            p_data["opciones"].append({
                "id": opcion.id,
                "texto": opcion.texto,
                "letra": opcion.letra,
                # NO enviamos es_correcta al estudiante
            })
        data["preguntas"].append(p_data)

    return Response(data)


@api_view(['POST'])
def iniciar_intento_examen(request):
    """
    Registra que un estudiante inició un examen.
    Payload: { id_examen, id_estudiante }
    """
    id_examen = request.data.get('id_examen')
    id_estudiante = request.data.get('id_estudiante')

    try:
        examen = Examen.objects.get(pk=id_examen, activo=True)
        estudiante = Usuario.objects.get(pk=id_estudiante)
    except (Examen.DoesNotExist, Usuario.DoesNotExist):
        return Response({"error": "Examen o estudiante no encontrado"}, status=404)

    # Verificar si ya tiene un intento
    intento_existente = IntentoExamen.objects.filter(
        examen=examen, estudiante=estudiante
    ).first()

    if intento_existente:
        if intento_existente.completado:
            return Response({"error": "Ya completaste este examen"}, status=400)
        serializer = IntentoExamenSerializer(intento_existente)
        return Response(serializer.data)

    intento = IntentoExamen.objects.create(
        examen=examen,
        estudiante=estudiante,
    )

    registrar_xapi(
        id_estudiante,
        "inició_examen",
        f"Examen '{examen.titulo}' (ID: {examen.id})"
    )

    serializer = IntentoExamenSerializer(intento)
    return Response(serializer.data, status=201)


@api_view(['POST'])
def enviar_respuestas_examen(request):
    """
    Recibe las respuestas del estudiante, califica y guarda.
    Payload: { id_intento, respuestas: [ { id_pregunta, id_opcion_elegida } ] }
    """
    id_intento = request.data.get('id_intento')
    respuestas = request.data.get('respuestas', [])

    try:
        intento = IntentoExamen.objects.get(pk=id_intento)
    except IntentoExamen.DoesNotExist:
        return Response({"error": "Intento no encontrado"}, status=404)

    if intento.completado:
        return Response({"error": "Este examen ya fue completado"}, status=400)

    total_preguntas = intento.examen.preguntas.count()
    correctas = 0

    with transaction.atomic():
        for resp in respuestas:
            id_pregunta = resp.get('id_pregunta')
            id_opcion = resp.get('id_opcion_elegida')

            try:
                pregunta = Pregunta.objects.get(pk=id_pregunta)
                opcion = Opcion.objects.get(pk=id_opcion) if id_opcion else None
            except (Pregunta.DoesNotExist, Opcion.DoesNotExist):
                continue

            es_correcta = opcion.es_correcta if opcion else False
            if es_correcta:
                correctas += 1

            RespuestaEstudiante.objects.update_or_create(
                intento=intento,
                pregunta=pregunta,
                defaults={
                    'opcion_elegida': opcion,
                    'es_correcta': es_correcta,
                }
            )

        calificacion = (correctas / total_preguntas * 100) if total_preguntas > 0 else 0
        intento.calificacion = round(calificacion, 2)
        intento.completado = True
        intento.fecha_fin = timezone.now()
        intento.save()

    registrar_xapi(
        intento.estudiante.id,
        "completó_examen",
        f"Examen '{intento.examen.titulo}' | Calificación: {intento.calificacion}% | "
        f"Correctas: {correctas}/{total_preguntas}"
    )

    return Response({
        "msg": "Examen calificado",
        "calificacion": intento.calificacion,
        "correctas": correctas,
        "total": total_preguntas,
    })


@api_view(['GET'])
def resultados_examen_estudiante(request, id_intento):
    """Devuelve el detalle de un intento: respuestas, qué eligió, qué era correcto."""
    try:
        intento = IntentoExamen.objects.get(pk=id_intento)
    except IntentoExamen.DoesNotExist:
        return Response({"error": "Intento no encontrado"}, status=404)

    data = {
        "examen": intento.examen.titulo,
        "calificacion": intento.calificacion,
        "fecha_inicio": intento.fecha_inicio,
        "fecha_fin": intento.fecha_fin,
        "respuestas": []
    }

    for resp in intento.respuestas.all().select_related('pregunta', 'opcion_elegida'):
        opcion_correcta = resp.pregunta.opciones.filter(es_correcta=True).first()
        data["respuestas"].append({
            "pregunta": resp.pregunta.texto,
            "opcion_elegida": resp.opcion_elegida.texto if resp.opcion_elegida else "Sin respuesta",
            "opcion_correcta": opcion_correcta.texto if opcion_correcta else "N/A",
            "es_correcta": resp.es_correcta,
        })

    return Response(data)