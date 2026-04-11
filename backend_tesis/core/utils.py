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

def generar_plantilla_cpp(nombre_clase, atributos=[], metodos=[], nombre_padre=None, atributos_padre=[], metodos_padre=[], codigo_viejo={}):
    """
    Genera una clase C++ completa con soporte para herencia, listas de inicialización y sobreescritura.
    """
    codigo = []
    codigo.append("#pragma once")
    # 1. INCLUDES BÁSICOS
    codigo.append("#include <iostream>")
    codigo.append("#include <string>")

    if nombre_padre:
        codigo.append(f'#include "{nombre_padre}.cpp"')

    codigo.append("using namespace std;")
    codigo.append("")

    # 2. DEFINICIÓN DE LA CLASE
    if nombre_padre:
        codigo.append(f"class {nombre_clase} : public {nombre_padre} {{")
    else:
        codigo.append(f"class {nombre_clase} {{")

    # Organizaremos por visibilidad (estilo C++)
    secciones = {'private': [], 'protected': [], 'public': []}

    # 3. ATRIBUTOS
    for attr in atributos:
        vis = getattr(attr, 'nivel', 'private')
        tipo = getattr(attr, 'tipo', 'string')
        # Ajuste de tipos comunes de Java a C++
        if tipo.lower() == 'string': tipo = 'string'
        if tipo.lower() == 'boolean': tipo = 'bool'
        
        nom = getattr(attr, 'nombre', 'var')
        secciones[vis].append(f"    {tipo} {nom};")

    # 4. MÉTODOS Y CONSTRUCTORES (Siempre en public para este ejemplo)
    
    # A) Constructor Vacío
    cons_vacio = f"    {nombre_clase}()"
    if nombre_padre:
        cons_vacio += f" : {nombre_padre}() {{}}"
    else:
        cons_vacio += " {}"
    secciones['public'].append("// --- Constructores ---")
    secciones['public'].append(cons_vacio)

    # B) Constructor con Argumentos
    args_cons = []
    init_list = []
    super_args = []

    if atributos_padre:
        for attr in atributos_padre:
            tipo = getattr(attr, 'tipo', 'string')
            nom = getattr(attr, 'nombre', 'p_var')
            args_cons.append(f"{tipo} {nom}")
            super_args.append(nom)

    for attr in atributos:
        tipo = getattr(attr, 'tipo', 'string')
        nom = getattr(attr, 'nombre', 'var')
        args_cons.append(f"{tipo} {nom}")
        init_list.append(f"{nom}({nom})")

    firma_cons = f"    {nombre_clase}({', '.join(args_cons)})"
    
    # Construcción de la lista de inicialización (estilo C++)
    elementos_init = []
    if nombre_padre and super_args:
        elementos_init.append(f"{nombre_padre}({', '.join(super_args)})")
    if init_list:
        elementos_init.extend(init_list)
    
    if elementos_init:
        firma_cons += " : " + ", ".join(elementos_init)
    
    secciones['public'].append(firma_cons + " {}")
    secciones['public'].append("")

    # 5. MÉTODOS PROPIOS
    if metodos:
        secciones['public'].append("    // --- Métodos Propios ---")
        for met in metodos:
            tipo = getattr(met, 'tipo', 'void')
            nom_raw = getattr(met, 'nombre', 'metodo')
            
            # Normalización
            nombre_limpio = nom_raw.split('(')[0].strip() if '(' in nom_raw else nom_raw
            firma = nom_raw if '(' in nom_raw else f"{nom_raw}()"

            metodo_str = [f"    virtual {tipo} {firma} {{"] # 'virtual' para permitir herencia
            if nombre_limpio in codigo_viejo:
                metodo_str.append(f"        {codigo_viejo[nombre_limpio]}")
            elif tipo != 'void':
                val = "0" if tipo in ['int','float','double'] else '""'
                metodo_str.append(f"        return {val};")
            metodo_str.append("    }")
            secciones['public'].append("\n".join(metodo_str))

    # 6. MÉTODOS HEREDADOS (Override)
    if nombre_padre and metodos_padre:
        secciones['public'].append(f"    // --- Sobreescritura de {nombre_padre} ---")
        for met in metodos_padre:
            if getattr(met, 'nivel', 'public') in ['public', 'protected']:
                tipo = getattr(met, 'tipo', 'void')
                nom_raw = getattr(met, 'nombre', 'metodo')
                nombre_limpio = nom_raw.split('(')[0].strip() if '(' in nom_raw else nom_raw
                firma = nom_raw if '(' in nom_raw else f"{nom_raw}()"

                over_str = [f"    {tipo} {firma} override {{"]
                over_str.append(f"        // Lógica de sobreescritura")
                if tipo == 'void':
                    over_str.append(f"        {nombre_padre}::{nombre_limpio}();")
                else:
                    over_str.append(f"        return {nombre_padre}::{nombre_limpio}();")
                over_str.append("    }")
                secciones['public'].append("\n".join(over_str))

    # ENSAMBLADO FINAL
    for vis in ['private', 'protected', 'public']:
        if secciones[vis]:
            codigo.append(f"{vis}:")
            codigo.extend(secciones[vis])
            codigo.append("")

    codigo.append("};") # C++ requiere punto y coma al final
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
        if(clase.id_proyecto.lenguaje == 'java'):
            nuevo_codigo = generar_plantilla_java(
                nombre_clase=clase.nombre, 
                atributos=mis_atributos, 
                metodos=mis_metodos,
                nombre_padre=nombre_padre,
                atributos_padre=atributos_heredados_completos,
                metodos_padre=metodos_padre,
                codigo_viejo=codigo_viejo
            )
        else:
            nuevo_codigo = generar_plantilla_cpp(
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
        ruta = guardar_archivo_fisico(uid, clase.id_proyecto.id, clase.nombre, nuevo_codigo, clase.id_proyecto.lenguaje)

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
    
import os

def actualizar_codigo_main(usuario_id, proyecto_id, nombre_clase, lenguaje):
    """
    Localiza el archivo Main e inyecta la nueva clase.
    Si nombre_clase llega vacío, solo asegura la existencia del Main base.
    """
    # 1. Construcción de rutas dinámicas
    ruta_relativa_carpeta = os.path.join('codigos_fuente', f'usuario_{usuario_id}', f'proyecto_{proyecto_id}')
    ruta_absoluta_carpeta = os.path.join(settings.BASE_DIR, ruta_relativa_carpeta)
    
    extension = '.cpp' if lenguaje == 'cpp' else '.java'
    nombre_archivo = f"Main{extension}"
    ruta_absoluta_archivo = os.path.join(ruta_absoluta_carpeta, nombre_archivo)

    # 2. Crear la estructura base si no existe (indispensable para el arranque)
    if not os.path.exists(ruta_absoluta_archivo):
        if not os.path.exists(ruta_absoluta_carpeta):
            os.makedirs(ruta_absoluta_carpeta)
            
        with open(ruta_absoluta_archivo, 'w', encoding='utf-8') as f:
            if lenguaje == 'cpp':
                # Incluimos el #pragma once que acordamos para evitar redefiniciones
                f.write('#pragma once\n#include <iostream>\nusing namespace std;\n\nint main() {\n    return 0;\n}')
            else:
                f.write('public class Main {\n    public static void main(String[] args) {\n    }\n}')

    # --- VALIDACIÓN DE NOMBRE VACÍO ---
    # Si no hay nombre de clase (clase inicial o Main recién creado), 
    # terminamos aquí para no insertar basura.
    if not nombre_clase or nombre_clase.strip() == "":
        return

    # 3. Configuración de la línea a inyectar
    if lenguaje == 'cpp':
        nueva_linea = f'#include "{nombre_clase}.cpp"'
        ancla = "using namespace std;"
    else:
        nueva_linea = f"// Clase {nombre_clase} vinculada"
        ancla = "public class Main {"

    # 4. Leer e Inyectar quirúrgicamente
    with open(ruta_absoluta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Evitar duplicados (idempotencia)
    if any(nueva_linea in linea for linea in lineas):
        return 

    nuevo_contenido = []
    insertado = False
    for linea in lineas:
        nuevo_contenido.append(linea)
        if ancla in linea and not insertado:
            nuevo_contenido.append(f"{nueva_linea}\n")
            insertado = True

    # 5. Guardar cambios respetando el código previo del alumno
    with open(ruta_absoluta_archivo, 'w', encoding='utf-8') as f:
        f.writelines(nuevo_contenido)

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
import os

def cosechar_codigo_existente(ruta_archivo):
    """
    Lee un archivo (Java o C++) y devuelve un diccionario con los cuerpos de los métodos.
    """
    if not os.path.exists(ruta_archivo):
        return {}

    codigo_preservado = {}
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Regex mejorada para C++ y Java:
        # 1. Soporta opcionalmente modificadores (public, virtual, static, etc.)
        # 2. Soporta tipos de retorno con punteros o referencias (char*, int&)
        # 3. Captura el nombre del método en el grupo 2
        patron = r'(?:[\w\s]+)?\s*[\w<>\[\]*&:]+\s+(\w+)\s*\([^)]*\)\s*(?:override|final)?\s*\{'
        
        for match in re.finditer(patron, contenido):
            nombre_metodo = match.group(1) # Ahora es el grupo 1 el nombre
            inicio_cuerpo = match.end()

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
            
            # Guardamos el cuerpo sin espacios en blanco innecesarios al inicio/final
            codigo_preservado[nombre_metodo] = cuerpo.strip('\n\r')

    except Exception as e:
        print(f"Error cosechando código en {ruta_archivo}: {e}")
    
    return codigo_preservado

def obtener_padre_desde_codigo(ruta_completa, lenguaje):
    if not os.path.exists(ruta_completa):
        return None
    
    try:
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if lenguaje.lower() == 'java':
            # Busca: public class Hijo extends Padre
            match = re.search(r'class\s+\w+\s+extends\s+(\w+)', contenido)
        else:
            # Busca: class Hijo : public Padre
            match = re.search(r'class\s+\w+\s*:\s*public\s+(\w+)', contenido)
            
        return match.group(1) if match else None
    except Exception:
        return None

def eliminar_vinculo_main(usuario_id, proyecto_id, nombre_clase, lenguaje):
    """
    Busca y elimina la línea de vinculación de una clase en el archivo Main.
    """
    # 1. Construcción de ruta (idéntica a la de creación)
    ruta_relativa = os.path.join('codigos_fuente', f'usuario_{usuario_id}', f'proyecto_{proyecto_id}')
    ruta_absoluta_carpeta = os.path.join(settings.BASE_DIR, ruta_relativa)
    
    extension = '.cpp' if lenguaje == 'cpp' else '.java'
    ruta_archivo = os.path.join(ruta_absoluta_carpeta, f"Main{extension}")

    # Si por alguna razón el Main no existe, no hay nada que limpiar
    if not os.path.exists(ruta_archivo):
        return

    # 2. Definir qué línea estamos buscando para borrar
    if lenguaje == 'cpp':
        linea_a_borrar = f'#include "{nombre_clase}.cpp"'
    else:
        linea_a_borrar = f"// Clase {nombre_clase} vinculada"

    # 3. Leer y filtrar
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Creamos una nueva lista de líneas EXCLUYENDO la que queremos borrar
    # Usamos .strip() para comparar sin preocuparnos por saltos de línea
    nuevas_lineas = [l for l in lineas if linea_a_borrar not in l]

    # 4. Guardar el archivo limpio
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.writelines(nuevas_lineas)

def inyectar_elemento_en_codigo(ruta_archivo, nuevo_contenido, lenguaje, es_metodo=False):
    """
    Inserta un atributo o método en el archivo físico sin alterar el resto del código.
    Inserta ANTES del último cierre de la clase (} o };) para evitar desplazar código.
    """
    if not os.path.exists(ruta_archivo):
        return False

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Evitar duplicados: Si el elemento ya existe, no hacemos nada
    if any(nuevo_contenido.strip() in l.strip() for l in lineas):
        return True

    # Buscar la ÚLTIMA llave de cierre de la clase (} para Java, }; para C++)
    indice_cierre = -1
    for i in range(len(lineas) - 1, -1, -1):
        linea_strip = lineas[i].strip()
        if lenguaje == 'cpp' and linea_strip == '};':
            indice_cierre = i
            break
        elif lenguaje != 'cpp' and linea_strip == '}':
            indice_cierre = i
            break

    if indice_cierre == -1:
        return False

    # Construir la línea a insertar con indentación correcta
    if es_metodo:
        linea_nueva = f"\n    {nuevo_contenido}\n\n"
    else:
        linea_nueva = f"    {nuevo_contenido}\n"

    # Insertar ANTES de la llave de cierre
    lineas.insert(indice_cierre, linea_nueva)

    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.writelines(lineas)
    
    return True