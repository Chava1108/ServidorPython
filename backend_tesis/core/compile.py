import os
import subprocess
import sys

def compilar_cpp(ruta_absoluta, archivos_cpp, entradas_usuario):
    """
    Maneja toda la lógica de C++: Compilación con g++, ejecución y limpieza.
    """
    # 1. Definir nombre del ejecutable según OS
    nombre_exe = "main_app.exe" if os.name == 'nt' else "./main_app"
    
    # 2. COMPILACIÓN
    comando_compile = ['g++'] + archivos_cpp + ['-o', nombre_exe]
    
    try:
        proceso_compile = subprocess.run(
            comando_compile,
            cwd=ruta_absoluta,
            capture_output=True,
            text=True,
            timeout=15
        )
    except subprocess.TimeoutExpired:
        return {"exito": False, "mensaje": "⏱️ Error: La compilación de C++ tardó demasiado."}

    if proceso_compile.returncode != 0:
        return {
            "exito": False, 
            "tipo_error": "compilacion",
            "mensaje": "❌ Error de Compilación C++:\n" + proceso_compile.stderr
        }

    # 3. EJECUCIÓN
    try:
        cmd_ejecucion = [os.path.join(ruta_absoluta, nombre_exe)] if os.name == 'nt' else [nombre_exe]
        
        proceso_run = subprocess.run(
            cmd_ejecucion,
            cwd=ruta_absoluta,
            capture_output=True,
            input=entradas_usuario,
            text=True,
            timeout=10
        )
        
        salida = proceso_run.stdout
        if proceso_run.stderr:
            salida += "\n⚠️ Salida de error (stderr):\n" + proceso_run.stderr

        resultado = {"exito": True, "mensaje": salida}

    except subprocess.TimeoutExpired:
        resultado = {"exito": False, "tipo_error": "tiempo", "mensaje": "⏱️ Timeout: El programa C++ tardó demasiado en ejecutarse."}
    
    # 4. LIMPIEZA (Borrar el .exe)
    ruta_exe_borrar = os.path.join(ruta_absoluta, nombre_exe)
    if os.path.exists(ruta_exe_borrar):
        try:
            os.remove(ruta_exe_borrar)
        except:
            pass

    return resultado


def compilar_java(ruta_absoluta, archivos_java, entradas_usuario):
    """
    Maneja toda la lógica de Java: Compilación con javac y ejecución con java.
    """
    # 1. COMPILACIÓN
    comando_compile = ['javac', '-encoding', 'utf-8'] + archivos_java
    
    try:
        proceso_compile = subprocess.run(
            comando_compile,
            cwd=ruta_absoluta,
            capture_output=True,
            text=True,
            timeout=15
        )
    except subprocess.TimeoutExpired:
        return {"exito": False, "mensaje": "⏱️ Error: La compilación de Java tardó demasiado."}

    if proceso_compile.returncode != 0:
        return {
            "exito": False, 
            "tipo_error": "compilacion",
            "mensaje": "❌ Error de Compilación Java:\n" + proceso_compile.stderr
        }

    # 2. VALIDAR MAIN
    if "Main.java" not in archivos_java:
        return {"exito": False, "tipo_error": "estructura", "mensaje": "⚠️ Compiló bien, pero falta 'Main.java' para ejecutar."}

    # 3. EJECUCIÓN
    try:
        proceso_run = subprocess.run(
            ['java', '-cp', '.', 'Main'], 
            cwd=ruta_absoluta,
            capture_output=True, 
            input=entradas_usuario,
            text=True,
            timeout=10
        )
        
        salida = proceso_run.stdout
        if proceso_run.stderr:
            salida += "\n⚠️ Errores ejecución:\n" + proceso_run.stderr

        return {"exito": True, "mensaje": salida}

    except subprocess.TimeoutExpired:
        return {"exito": False, "tipo_error": "tiempo", "mensaje": "⏱️ Timeout: El programa Java tardó demasiado."}