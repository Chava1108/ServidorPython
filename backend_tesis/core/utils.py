import javalang
import os
from django.conf import settings
from .models import Clase, Atributos, Funciones, LogActividad, Proyecto, Herencia
import re
from rest_framework.exceptions import ValidationError

def analizar_codigo_java(codigo_fuente):
    """
    Recibe un string con código Java y devuelve un diccionario 
    con la estructura para el diagrama.
    """
    resultado = {
        "clases": [],
        "errores": []
    }

    try:
        tree = javalang.parse.parse(codigo_fuente)

        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            clase_info = {
                "nombre": node.name,
                "padre": node.extends.name if node.extends else None, # Detectar herencia
                "atributos": [],
                "metodos": []
            }

            for field in node.fields:
                tipo = field.type.name
                for declarator in field.declarators:
                    clase_info["atributos"].append({
                        "nombre": declarator.name,
                        "tipo": tipo,
                        "visibilidad": "public" if "public" in field.modifiers else "private"
                    })

            for method in node.methods:
                clase_info["metodos"].append({
                    "nombre": method.name,
                    "retorno": method.return_type.name if method.return_type else "void",
                    "visibilidad": "public" if "public" in method.modifiers else "private"
                })

            resultado["clases"].append(clase_info)

    except javalang.parser.JavaSyntaxError as e:
        # Si el alumno escribió mal el código, capturamos el error
        resultado["errores"].append(f"Error de sintaxis en la línea {e.description.line}: {e.description}")
    except Exception as e:
        resultado["errores"].append(str(e))

    return resultado

def generar_plantilla_java(nombre_clase, atributos=[], metodos=[], nombre_padre=None, atributos_padre=[], metodos_padre=[], codigo_viejo={}):
    """
    Genera una clase Java completa con soporte para herencia, constructores y sobreescritura.
    """
    codigo = []
    print("--- INSPECCIONANDO MÉTODOS ---")
    for m in metodos:
        print(f"Nombre: {m.nombre}, Tipo: {getattr(m, 'tipo', 'N/A')}")

    # 1. DEFINICIÓN DE LA CLASE
    if nombre_padre:
        codigo.append(f"public class {nombre_clase} extends {nombre_padre} {{")
    else:
        codigo.append(f"public class {nombre_clase} {{")
    
    codigo.append("") 

    # 2. ATRIBUTOS PROPIOS
    if atributos:
        codigo.append("    // --- Atributos Propios ---")
        for attr in atributos:
            vis = getattr(attr, 'nivel', 'private') 
            tipo = getattr(attr, 'tipo', 'String')
            nom = getattr(attr, 'nombre', 'sin_nombre')
            codigo.append(f"    {vis} {tipo} {nom};")
        codigo.append("")

    # 3. CONSTRUCTORES
    codigo.append("    // --- Constructores ---")
    
    # A) Constructor Vacío
    codigo.append(f"    public {nombre_clase}() {{")
    if nombre_padre:
        codigo.append("        super(); // Llama al constructor del padre")
    codigo.append("    }")
    codigo.append("")

    # B) Constructor con Argumentos (Padre + Hijo)
    # Recopilamos todos los argumentos necesarios
    args_constructor = []
    super_args = []
    
    # Primero los del padre (para el super)
    if atributos_padre:
        for attr in atributos_padre:
            tipo = getattr(attr, 'tipo', 'String')
            nom = getattr(attr, 'nombre', 'var')
            args_constructor.append(f"{tipo} {nom}")
            super_args.append(nom)
            
    # Luego los propios (para el this)
    own_args_names = []
    for attr in atributos:
        tipo = getattr(attr, 'tipo', 'String')
        nom = getattr(attr, 'nombre', 'var')
        args_constructor.append(f"{tipo} {nom}")
        own_args_names.append(nom)

    # Generamos la firma del constructor completo
    firma_args = ", ".join(args_constructor)
    codigo.append(f"    public {nombre_clase}({firma_args}) {{")
    
    # Cuerpo del constructor
    if nombre_padre and atributos_padre:
        codigo.append(f"        super({', '.join(super_args)}); // Inicializa atributos del padre")
    elif nombre_padre:
        codigo.append("        super();")
        
    for nom in own_args_names:
        codigo.append(f"        this.{nom} = {nom};")
        
    codigo.append("    }")
    codigo.append("")

# --- MÉTODOS PROPIOS ---
# 4. MÉTODOS PROPIOS
    if metodos:
        codigo.append("    // --- Métodos Propios ---")
        for met in metodos:
            vis = getattr(met, 'nivel', 'public') # o 'nivel'
            tipo = getattr(met, 'tipo', 'void')
            nom_raw = getattr(met, 'nombre', 'sin_nombre')

            # --- NORMALIZACIÓN DEL NOMBRE ---
            # Queremos asegurar que 'firma' tenga paréntesis y 'nombre_limpio' NO los tenga.
            if '(' in nom_raw:
                firma = nom_raw  # Ej: "ladrar(int a)"
                nombre_limpio = nom_raw.split('(')[0].strip() # Ej: "ladrar"
            else:
                firma = f"{nom_raw}()" # Ej: "ladrar()"
                nombre_limpio = nom_raw # Ej: "ladrar"

            # Generamos la definición usando la FIRMA (con paréntesis)
            codigo.append(f"    {vis} {tipo} {firma} {{")
            
            # Buscamos en el código viejo usando el NOMBRE LIMPIO
            if nombre_limpio in codigo_viejo:
                codigo.append(codigo_viejo[nombre_limpio])
            else:
                # Default
                if tipo != 'void':
                    val = "0" if tipo in ['int','double','float'] else "null"
                    if tipo == 'boolean': val = "false"
                    codigo.append(f"        return {val};")
                    
            codigo.append("    }")
            codigo.append("")

    # 5. MÉTODOS HEREDADOS
    if nombre_padre and metodos_padre:
        codigo.append(f"    // --- Métodos heredados de {nombre_padre} (Ejemplo de sobreescritura) ---")
        for met in metodos_padre:
            vis = getattr(met, 'nivel', 'public') # o 'nivel'
            
            if vis in ['protected', 'public']:
                tipo = getattr(met, 'tipo', 'void')
                nom_raw = getattr(met, 'nombre', 'sin_nombre')
                
                # --- MISMA NORMALIZACIÓN ---
                if '(' in nom_raw:
                    firma = nom_raw
                    nombre_limpio = nom_raw.split('(')[0].strip()
                else:
                    firma = f"{nom_raw}()"
                    nombre_limpio = nom_raw
                
                codigo.append("    @Override")
                # Usamos FIRMA para definir
                codigo.append(f"    {vis} {tipo} {firma} {{")
                codigo.append(f"        // Puedes agregar lógica extra aquí")
                
                # --- CORRECCIÓN DE LA LLAMADA A SUPER ---
                # Usamos nombre_limpio + () 
                # NOTA: Esto asume métodos sin argumentos. Si tienen argumentos (int a), 
                # pasar 'super.metodo(int a)' es error de Java. 
                # Para Tesis básica, dejaremos 'super.metodo()' o 'super.metodo(args_dummy)'
                
                llamada_super = f"super.{nombre_limpio}()" 

                if tipo == 'void':
                    codigo.append(f"        {llamada_super}; // Llama a la versión del padre")
                else:
                    codigo.append(f"        return {llamada_super};")
                    
                codigo.append("    }")
                codigo.append("")

    codigo.append("}")
    return "\n".join(codigo)

# core/utils.py

def propagar_cambios_a_hijos(id_clase_padre):
    """
    Busca todas las clases que heredan de 'id_clase_padre' 
    y regenera sus archivos para que reflejen los cambios del padre.
    """
    # 1. Buscar en la tabla Herencia quiénes son los hijos
    hijos_relacion = Herencia.objects.filter(id_clasePadre=id_clase_padre)
    
    if not hijos_relacion:
        return # Caso base: Si no tiene hijos, termina la recursión.

    print(f"--- Propagando cambios de Clase ID {id_clase_padre} a {len(hijos_relacion)} hijos ---")

    for relacion in hijos_relacion:
        id_hijo = relacion.id_claseHijo.pk
        
        # 2. Regenerar el archivo del hijo
        # Esto automáticamente leerá los nuevos atributos del padre de la BD
        actualizar_archivo_java_desde_bd(id_hijo)

def guardar_archivo_fisico(usuario_id, proyecto_id, nombre_clase, codigo_texto, lenguaje):
    ruta_relativa_carpeta = os.path.join('codigos_fuente', f'usuario_{usuario_id}', f'proyecto_{proyecto_id}')
    ruta_absoluta_carpeta = os.path.join(settings.BASE_DIR, ruta_relativa_carpeta)
    
    if not os.path.exists(ruta_absoluta_carpeta):
        os.makedirs(ruta_absoluta_carpeta)
    extension = '.cpp' if lenguaje == 'cpp' else '.java'
    nombre_archivo = f"{nombre_clase}{extension}"
    ruta_absoluta_archivo = os.path.join(ruta_absoluta_carpeta, nombre_archivo)
    
    with open(ruta_absoluta_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write(codigo_texto)
        
    return os.path.join(ruta_relativa_carpeta, nombre_archivo)
# core/utils.py

def actualizar_archivo_java_desde_bd(id_clase):
    try:
        # 1. Obtener datos propios
        clase = Clase.objects.get(pk=id_clase)
        mis_atributos = Atributos.objects.filter(id_clase=id_clase)
        mis_metodos = Funciones.objects.filter(id_clase=id_clase)

        # 2. Obtener datos del PADRE (Si existe)
        nombre_padre = None
        atributos_heredados_completos = []
        metodos_padre = []
        codigo_viejo = {}

        print("--- INSPECCIONANDO MÉTODOS ---")
        for m in mis_metodos:
            print(f"Nombre: {m.nombre}, Tipo: {getattr(m, 'tipo', 'N/A')}")

        if clase.path_archivo and os.path.exists(clase.path_archivo):
            codigo_viejo = cosechar_codigo_existente(clase.path_archivo)

        try:
            relacion = Herencia.objects.get(id_claseHijo=id_clase)
            clase_padre = relacion.id_clasePadre
            nombre_padre = clase_padre.nombre
            

            atributos_heredados_completos = obtener_atributos_ancestrales(id_clase)


            metodos_padre = Funciones.objects.filter(
                id_clase=clase_padre.pk
            ).exclude(nivel='private') 

        except Herencia.DoesNotExist:
            pass # No tiene padre

        # 3. Generar Código
        nuevo_codigo = generar_plantilla_java(
            nombre_clase=clase.nombre, 
            atributos=mis_atributos, 
            metodos=mis_metodos,
            nombre_padre=nombre_padre,
            atributos_padre=atributos_heredados_completos,
            metodos_padre=metodos_padre,
            codigo_viejo=codigo_viejo
        )

        # 4. Guardar archivo físico
        uid = clase.id_proyecto.id_usr.id if hasattr(clase.id_proyecto.id_usr, 'id') else clase.id_proyecto.id_usr
        ruta = guardar_archivo_fisico(uid, clase.id_proyecto.id, clase.nombre, nuevo_codigo)

        clase.path_archivo = ruta
        clase.save()

        # --- PASO CRÍTICO: REACCIÓN EN CADENA ---
        # Una vez que yo (Padre) me actualicé, aviso a mis hijos para que se actualicen ellos
        propagar_cambios_a_hijos(id_clase)
        # ----------------------------------------
        
        return True
    except Exception as e:
        print(f"Error regenerando archivo ID {id_clase}: {e}")
        return False
    
def generar_codigo_main(lenguaje):
    codigo = ""
    if lenguaje == 'cpp':
        codigo = '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hola Mundo C++" << endl;\n    return 0;\n}'
    else:
        codigo = """public class Main {
            public static void main(String[] args) {
                // Instancia tus clases aquí y prueba tus métodos
                System.out.println("Hola Mundo desde el Main!");
            }
            }"""
    return codigo

def registrar_xapi(actor, verbo, objeto=""):
    print(f"Entro a guardarLog actor: {actor}, verbo: {verbo}")
    try:
        LogActividad.objects.create(
            usuario=int(actor), # Aseguramos que se guarde como texto
            accion=verbo,
            detalle=objeto
        )
        print("DEBUG: Log guardado con éxito (Método ForeignKey)")
    except Exception as e:
        print(f"Error guardando log xAPI: {e}")

import subprocess

def ejecutar_compilacion(ruta_carpeta, nombre_archivo):
    """
    Ejecuta 'javac' sobre el archivo en la carpeta dada.
    Retorna: (exito: bool, mensaje: str)
    """
    try:
        # Comando: javac -encoding utf8 NombreArchivo.java
        # cwd=ruta_carpeta hace que el comando se ejecute DENTRO de la carpeta del proyecto
        # Esto es vital para que reconozca las otras clases (Herencia, Main, etc.)
        proceso = subprocess.run(
            ['javac', '-encoding', 'utf-8', nombre_archivo],
            cwd=ruta_carpeta,
            capture_output=True,
            text=True
        )

        if proceso.returncode == 0:
            return True, "Compilación exitosa. No se encontraron errores de sintaxis."
        else:
            # Si falló, devolvemos el error (stderr)
            return False, proceso.stderr

    except Exception as e:
        return False, f"Error interno al intentar compilar: {str(e)}"
    
def procesar_nombre_metodo_java(nombre_raw):
    if not nombre_raw:
        return nombre_raw
    nombre_limpio = nombre_raw.strip()
    if '(' not in nombre_limpio:
        nombre_ajustado = f"{nombre_limpio}()"
    else:
        nombre_ajustado = nombre_limpio
        if not nombre_ajustado.endswith(')'):
            nombre_ajustado += ')'
    patron_java = r'^[a-zA-Z_$][a-zA-Z0-9_$]*\s*\(.*\)$'
    if not re.match(patron_java, nombre_ajustado):
        raise ValidationError(f"El nombre '{nombre_ajustado}' no es válido para un método Java.")

    return nombre_ajustado

def obtener_atributos_ancestrales(id_clase):
    """
    Recorre recursivamente hacia arriba (padres, abuelos...) 
    y retorna una lista ordenada de TODOS los atributos heredados.
    """
    atributos_acumulados = []

    try:
        relacion = Herencia.objects.get(id_claseHijo=id_clase)
        clase_padre = relacion.id_clasePadre
        atributos_abuelo = obtener_atributos_ancestrales(clase_padre.pk)
        atributos_acumulados.extend(atributos_abuelo)
        attrs_padre = Atributos.objects.filter(id_clase=clase_padre.pk)
        atributos_acumulados.extend(list(attrs_padre))
        
    except Herencia.DoesNotExist:
        return []
        
    return atributos_acumulados

import re

def cosechar_codigo_existente(ruta_archivo):
    """
    Lee un archivo Java y devuelve un diccionario:
    { "nombreMetodo": "contenido del cuerpo...", "constructor": "contenido..." }
    """
    if not os.path.exists(ruta_archivo):
        return {}

    codigo_preservado = {}
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()


        patron = r'(public|protected|private|static|\s) +[\w<>\[\]]+ +(\w+) *\([^)]*\) *\{'
        
        for match in re.finditer(patron, contenido):
            nombre_metodo = match.group(2) # El nombre capturado
            inicio_cuerpo = match.end() # Donde termina la llave {

            llaves_abiertas = 1
            cursor = inicio_cuerpo
            cuerpo = ""
            
            while cursor < len(contenido) and llaves_abiertas > 0:
                char = contenido[cursor]
                if char == '{':
                    llaves_abiertas += 1
                elif char == '}':
                    llaves_abiertas -= 1
                
                if llaves_abiertas > 0:
                    cuerpo += char
                cursor += 1
            
            # Guardamos el cuerpo limpio (sin la llave de cierre final)
            codigo_preservado[nombre_metodo] = cuerpo

    except Exception as e:
        print(f"Error cosechando código: {e}")
    
    return codigo_preservado