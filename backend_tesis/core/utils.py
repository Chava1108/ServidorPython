import javalang
import os
from django.conf import settings
from .models import Clase, LogActividad, Proyecto
import re
from rest_framework.exceptions import ValidationError


def analizar_archivo_clase(clase):
    """
    Analiza el archivo fuente de una clase y extrae atributos, funciones y padre.
    Funciona para Java y C++. Retorna dict con:
    {atributos: [...], funciones: [...], padre: str|None, errores: [...]}
    """
    resultado = {
        'atributos': [],
        'funciones': [],
        'padre': None,
        'errores': [],
    }

    if not clase.path_archivo:
        return resultado

    ruta = os.path.join(settings.BASE_DIR, clase.path_archivo)
    if not os.path.exists(ruta):
        resultado['errores'].append(f'Archivo no encontrado: {clase.path_archivo}')
        return resultado

    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        resultado['errores'].append(str(e))
        return resultado

    lenguaje = clase.id_proyecto.lenguaje if clase.id_proyecto else 'java'

    if lenguaje == 'java':
        return _analizar_java(contenido, resultado)
    else:
        return _analizar_cpp(contenido, resultado)


def _analizar_java(contenido, resultado):
    """Analiza código Java con javalang."""
    try:
        tree = javalang.parse.parse(contenido)
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            resultado['padre'] = node.extends.name if node.extends else None

            for field in node.fields:
                tipo = field.type.name
                modifiers = list(field.modifiers) if field.modifiers else []
                nivel = 'public' if 'public' in modifiers else ('protected' if 'protected' in modifiers else 'private')
                for declarator in field.declarators:
                    resultado['atributos'].append({
                        'nombre': declarator.name,
                        'tipo': tipo,
                        'nivel': nivel,
                    })

            for method in node.methods:
                modifiers = list(method.modifiers) if method.modifiers else []
                nivel = 'public' if 'public' in modifiers else ('protected' if 'protected' in modifiers else 'private')
                retorno = method.return_type.name if method.return_type else 'void'
                resultado['funciones'].append({
                    'nombre': method.name,
                    'tipo': retorno,
                    'nivel': nivel,
                })
            break  # Solo la primera clase del archivo
    except Exception as e:
        resultado['errores'].append(str(e))
        # Fallback con regex si javalang falla
        _analizar_java_regex(contenido, resultado)

    return resultado


def _analizar_java_regex(contenido, resultado):
    """Fallback regex-based Java parser."""
    # Padre
    m = re.search(r'class\s+\w+\s+extends\s+(\w+)', contenido)
    if m:
        resultado['padre'] = m.group(1)

    # Atributos: líneas con tipo nombre; (no métodos)
    for m in re.finditer(
        r'^\s*(public|private|protected)\s+'
        r'(?!(?:void|class|static\s+void|abstract)\b)'
        r'(\w+)\s+(\w+)\s*[;=]',
        contenido, re.MULTILINE
    ):
        resultado['atributos'].append({
            'nivel': m.group(1),
            'tipo': m.group(2),
            'nombre': m.group(3),
        })

    # Funciones: líneas con tipo nombre(
    for m in re.finditer(
        r'^\s*(public|private|protected)\s+(\w+)\s+(\w+)\s*\(',
        contenido, re.MULTILINE
    ):
        if m.group(3) not in [resultado.get('padre', ''), 'main']:
            resultado['funciones'].append({
                'nivel': m.group(1),
                'tipo': m.group(2),
                'nombre': m.group(3),
            })


def _analizar_cpp(contenido, resultado):
    """Analiza código C++ con regex."""
    # Padre: class Nombre : public Padre
    m = re.search(r'class\s+\w+\s*:\s*(?:public|protected|private)\s+(\w+)', contenido)
    if m:
        resultado['padre'] = m.group(1)

    # Encontrar el cuerpo de la clase
    class_match = re.search(r'class\s+\w+[^{]*\{', contenido)
    if not class_match:
        return resultado

    # Extraer contenido entre las llaves de la clase
    inicio = class_match.end()
    nivel_llaves = 1
    i = inicio
    while i < len(contenido) and nivel_llaves > 0:
        if contenido[i] == '{':
            nivel_llaves += 1
        elif contenido[i] == '}':
            nivel_llaves -= 1
        i += 1
    cuerpo_clase = contenido[inicio:i - 1]

    # Determinar sección actual (public/private/protected)
    seccion_actual = 'private'  # default en C++
    lineas = cuerpo_clase.split('\n')

    for linea in lineas:
        stripped = linea.strip()

        # Detectar cambio de sección
        sec_match = re.match(r'^(public|private|protected)\s*:', stripped)
        if sec_match:
            seccion_actual = sec_match.group(1)
            continue

        # Ignorar comentarios, líneas vacías, constructores, destructores
        if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue

        # Ignorar constructores: NombreClase(...)
        nombre_clase_match = re.search(r'class\s+(\w+)', contenido)
        nombre_clase = nombre_clase_match.group(1) if nombre_clase_match else ''
        if re.match(rf'^\s*{re.escape(nombre_clase)}\s*\(', stripped):
            continue
        if re.match(rf'^\s*~{re.escape(nombre_clase)}\s*\(', stripped):
            continue

        # Funciones: tipo nombre(...)
        func_match = re.match(
            r'(?:virtual\s+)?(\w+)\s+(\w+)\s*\([^)]*\)',
            stripped
        )
        if func_match:
            tipo = func_match.group(1)
            nombre = func_match.group(2)
            if nombre not in [nombre_clase, f'~{nombre_clase}', 'main']:
                resultado['funciones'].append({
                    'nombre': nombre,
                    'tipo': tipo,
                    'nivel': seccion_actual,
                })
            continue

        # Atributos: tipo nombre;
        attr_match = re.match(r'(\w+)\s+(\w+)\s*;', stripped)
        if attr_match:
            resultado['atributos'].append({
                'nombre': attr_match.group(2),
                'tipo': attr_match.group(1),
                'nivel': seccion_actual,
            })

    return resultado


def extraer_codigo_funcion_desde_archivo(ruta, nombre_funcion, tipo_retorno):
    """Extrae el código de una función desde un archivo fuente."""
    try:
        if not ruta or not os.path.exists(ruta):
            return ''
        with open(ruta, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()

        nombre_limpio = (nombre_funcion or '').replace('()', '').strip()
        tipo_limpio = (tipo_retorno or '').strip()

        if not nombre_limpio:
            return ''

        patron = re.compile(
            rf'(?:(?:public|protected|private|static|final|abstract|synchronized|native|virtual)\s+)*'
            rf'(?:{re.escape(tipo_limpio)}\s+)?'
            rf'{re.escape(nombre_limpio)}\s*\([^)]*\)\s*\{{',
            re.MULTILINE
        )
        match = patron.search(contenido)
        if not match:
            patron_simple = re.compile(
                rf'\b{re.escape(nombre_limpio)}\s*\([^)]*\)\s*\{{',
                re.MULTILINE
            )
            match = patron_simple.search(contenido)

        if not match:
            return ''

        inicio = match.start()
        nivel_llaves = 0
        i = match.end() - 1
        while i < len(contenido):
            if contenido[i] == '{':
                nivel_llaves += 1
            elif contenido[i] == '}':
                nivel_llaves -= 1
                if nivel_llaves == 0:
                    return contenido[inicio:i + 1]
            i += 1
        return contenido[inicio:]
    except Exception:
        return ''

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
    from .models import Usuario
    print(f"Entro a guardarLog actor: {actor}, verbo: {verbo}")
    try:
        # No registrar actividad de administradores para evitar ruido en analytics
        usuario_obj = Usuario.objects.filter(id=int(actor)).first()
        if usuario_obj and usuario_obj.is_admin:
            print("DEBUG: Log omitido (usuario es admin)")
            return
        LogActividad.objects.create(
            usuario=int(actor),
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

def inyectar_elemento_en_codigo(ruta_archivo, nuevo_contenido, lenguaje, es_metodo=False, nivel='public'):
    """
    Inserta un atributo o método en el archivo fuente.
    - Java: atributos antes del primer constructor/método, métodos antes del cierre.
    - C++: busca la sección correspondiente (public:/private:/protected:) y coloca
      atributos después de los existentes en esa sección, métodos al final de la sección.
      Si la sección no existe, la crea antes del cierre de la clase.
    """
    ruta_completa = os.path.join(settings.BASE_DIR, ruta_archivo) if ruta_archivo else None
    if not ruta_completa or not os.path.exists(ruta_completa):
        return False

    with open(ruta_completa, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Evitar duplicados
    if nuevo_contenido.strip() in contenido:
        return True

    lineas = contenido.split('\n')

    if lenguaje == 'cpp':
        exito = _inyectar_cpp(lineas, nuevo_contenido, es_metodo, nivel)
    else:
        exito = _inyectar_java(lineas, nuevo_contenido, es_metodo)

    if not exito:
        return False

    with open(ruta_completa, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas))

    return True


def _inyectar_java(lineas, nuevo_contenido, es_metodo):
    """Inyecta en archivo Java."""
    if es_metodo:
        indice = _encontrar_cierre_clase(lineas, 'java')
        if indice == -1:
            return False
        lineas.insert(indice, '')
        lineas.insert(indice + 1, f"    {nuevo_contenido}")
    else:
        indice = _encontrar_zona_atributos_java(lineas)
        if indice == -1:
            indice = _encontrar_cierre_clase(lineas, 'java')
            if indice == -1:
                return False
        lineas.insert(indice, f"    {nuevo_contenido}")
    return True


def _inyectar_cpp(lineas, nuevo_contenido, es_metodo, nivel):
    """
    Inyecta en archivo C++.
    Busca la sección correspondiente (public:/private:/protected:) y coloca
    el elemento en la posición correcta dentro de esa sección.
    """
    seccion_label = f"{nivel}:"

    # Buscar inicio de la clase
    inicio_clase = -1
    for i, linea in enumerate(lineas):
        if re.match(r'^\s*class\s+\w+', linea.strip()):
            inicio_clase = i
            break
    if inicio_clase == -1:
        return False

    # Buscar llave de apertura de la clase
    inicio_cuerpo = -1
    for i in range(inicio_clase, len(lineas)):
        if '{' in lineas[i]:
            inicio_cuerpo = i + 1
            break
    if inicio_cuerpo == -1:
        return False

    cierre_clase = _encontrar_cierre_clase(lineas, 'cpp')
    if cierre_clase == -1:
        return False

    # Buscar la sección correspondiente (e.g. "public:")
    seccion_inicio = -1
    for i in range(inicio_cuerpo, cierre_clase):
        if lineas[i].strip() == seccion_label:
            seccion_inicio = i
            break

    if seccion_inicio == -1:
        # La sección no existe: crearla al INICIO del cuerpo de la clase (convención C++)
        lineas.insert(inicio_cuerpo, f"{seccion_label}")
        lineas.insert(inicio_cuerpo + 1, f"    {nuevo_contenido}")
        return True

    # Encontrar el fin de esta sección (siguiente sección o cierre de clase)
    seccion_fin = cierre_clase
    for i in range(seccion_inicio + 1, cierre_clase):
        stripped = lineas[i].strip()
        if re.match(r'^(public|private|protected)\s*:', stripped):
            seccion_fin = i
            break

    if es_metodo:
        # Métodos: insertar al final de la sección, antes de la siguiente sección o cierre
        lineas.insert(seccion_fin, f"    {nuevo_contenido}")
        lineas.insert(seccion_fin, '')
    else:
        # Atributos: insertar después del último atributo en esta sección,
        # pero antes del primer constructor/método
        ultimo_atributo = -1
        primer_metodo = -1
        nivel_llaves = 0

        for i in range(seccion_inicio + 1, seccion_fin):
            stripped = lineas[i].strip()

            nivel_llaves += stripped.count('{') - stripped.count('}')
            if nivel_llaves > 0:
                continue

            if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue

            # Constructor o método: tiene paréntesis
            if re.match(r'.*\w+\s*\(', stripped):
                if primer_metodo == -1:
                    primer_metodo = i
                break

            # Atributo: termina en ; sin paréntesis
            if stripped.endswith(';') and '(' not in stripped:
                ultimo_atributo = i

        if ultimo_atributo != -1:
            lineas.insert(ultimo_atributo + 1, f"    {nuevo_contenido}")
        elif primer_metodo != -1:
            lineas.insert(primer_metodo, f"    {nuevo_contenido}")
        else:
            # Sección vacía o solo comentarios
            lineas.insert(seccion_inicio + 1, f"    {nuevo_contenido}")

    return True


def _encontrar_cierre_clase(lineas, lenguaje):
    """Encuentra el índice de la última llave de cierre de la clase."""
    cierre = '};' if lenguaje == 'cpp' else '}'
    for i in range(len(lineas) - 1, -1, -1):
        if lineas[i].strip() == cierre:
            return i
    return -1


def _encontrar_zona_atributos_java(lineas):
    """
    Para Java: busca la posición después del último atributo,
    o antes del primer constructor/método.
    """
    inicio_clase = -1
    for i, linea in enumerate(lineas):
        stripped = linea.strip()
        if re.match(r'^(public\s+)?class\s+\w+', stripped):
            inicio_clase = i
            break

    if inicio_clase == -1:
        return -1

    inicio_cuerpo = -1
    for i in range(inicio_clase, len(lineas)):
        if '{' in lineas[i]:
            inicio_cuerpo = i + 1
            break

    if inicio_cuerpo == -1:
        return -1

    ultimo_atributo = -1
    primer_metodo = -1
    nivel_llaves = 0

    for i in range(inicio_cuerpo, len(lineas)):
        stripped = lineas[i].strip()

        nivel_llaves += stripped.count('{') - stripped.count('}')

        if nivel_llaves > 0 and '{' in stripped and ('}' not in stripped or stripped.count('{') > stripped.count('}')):
            continue
        if nivel_llaves > 0:
            continue

        if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue

        # Constructor o método
        if re.match(r'.*\w+\s*\(', stripped) and primer_metodo == -1:
            primer_metodo = i
            break

        # Atributo
        if stripped.endswith(';') and '(' not in stripped:
            ultimo_atributo = i

    if ultimo_atributo != -1:
        return ultimo_atributo + 1
    if primer_metodo != -1:
        return primer_metodo
    return inicio_cuerpo