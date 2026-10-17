import os
import re
import shutil
import signal
import subprocess
import tempfile

# --- Límites de ejecución ---
TIEMPO_COMPILACION = 15            # segundos
TIEMPO_EJECUCION = 10              # segundos
LIMITE_SALIDA = 64 * 1024          # bytes de stdout/stderr que se devuelven al alumno
LIMITE_ARCHIVO = 10 * 1024 * 1024  # tamaño máximo de lo que el programa escribe (incluye su salida)
LIMITE_MEMORIA_CPP = 512 * 1024 * 1024
MEMORIA_JVM = "-Xmx256m"           # la JVM no tolera RLIMIT_AS; se limita con su propia opción

ES_POSIX = os.name == "posix"
if ES_POSIX:
    import resource

# g++ avisa esto en cada Main.cpp que conserva el "#pragma once" de proyectos anteriores
AVISO_PRAGMA = re.compile(r"^.*#pragma once in main file.*$\n?(^\s*\d*\s*\|.*$\n?)*", re.MULTILINE)


def _limites(segundos, memoria=None):
    """Devuelve la función que aplica límites al proceso hijo (solo Linux)."""
    if not ES_POSIX:
        return None

    def aplicar():
        os.setsid()  # grupo de procesos propio: al vencer el tiempo se termina también a sus hijos
        resource.setrlimit(resource.RLIMIT_CPU, (segundos + 1, segundos + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (LIMITE_ARCHIVO, LIMITE_ARCHIVO))
        if memoria:
            resource.setrlimit(resource.RLIMIT_AS, (memoria, memoria))
    return aplicar


def _leer(archivo):
    """Lee como máximo LIMITE_SALIDA bytes; indica si la salida se recortó."""
    archivo.seek(0, os.SEEK_END)
    total = archivo.tell()
    archivo.seek(0)
    texto = archivo.read(LIMITE_SALIDA).decode("utf-8", errors="replace")
    if total > LIMITE_SALIDA:
        texto += f"\n... (salida recortada: el programa imprimió {total // 1024} KB; se muestran los primeros {LIMITE_SALIDA // 1024} KB)"
    return texto


def _ejecutar(comando, cwd, entrada="", tiempo=TIEMPO_EJECUCION, memoria=None):
    """
    Ejecuta un comando escribiendo su salida en archivos temporales (nunca en memoria),
    con límite de tiempo y, en Linux, de CPU, tamaño de archivos y memoria.
    Devuelve (codigo_salida, stdout, stderr); codigo_salida es None si se agotó el tiempo.
    """
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        proceso = subprocess.Popen(
            comando, cwd=cwd, stdin=subprocess.PIPE, stdout=out, stderr=err,
            preexec_fn=_limites(tiempo, memoria),
        )
        try:
            proceso.communicate(input=(entrada or "").encode("utf-8"), timeout=tiempo)
            codigo = proceso.returncode
        except subprocess.TimeoutExpired:
            if ES_POSIX:
                try:
                    os.killpg(proceso.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                proceso.kill()
            proceso.wait()
            codigo = None
        return codigo, _leer(out), _leer(err)


def _motivo_terminacion(codigo):
    """Traduce las señales de los límites a un mensaje para el alumno."""
    if ES_POSIX and codigo == -signal.SIGXFSZ:
        return f"\n⚠️ El programa se detuvo: su salida superó {LIMITE_ARCHIVO // (1024 * 1024)} MB."
    if ES_POSIX and codigo == -signal.SIGXCPU:
        return "\n⏱️ El programa se detuvo: superó el tiempo de CPU permitido."
    if codigo is not None and codigo < 0:
        return f"\n⚠️ El programa terminó de forma anormal (señal {-codigo})."
    return ""


def compilar_cpp(ruta_absoluta, archivos_cpp, entradas_usuario):
    """
    Compila y ejecuta un proyecto C++.
    Solo se compila Main.cpp: ya incluye cada clase con #include "Clase.cpp".
    Compilar también cada .cpp por separado duplica las definiciones de los métodos
    escritos fuera de la clase ("multiple definition").
    """
    if "Main.cpp" not in archivos_cpp:
        return {"exito": False, "tipo_error": "estructura",
                "mensaje": "⚠️ Falta 'Main.cpp' en el proyecto: es el punto de entrada del programa."}

    # Carpeta temporal única: dos ejecuciones simultáneas no comparten el ejecutable
    carpeta_tmp = tempfile.mkdtemp(prefix="poograph_")
    nombre_exe = "main_app.exe" if os.name == "nt" else "main_app"
    ejecutable = os.path.join(carpeta_tmp, nombre_exe)
    try:
        codigo, _, errores = _ejecutar(["g++", "Main.cpp", "-o", ejecutable],
                                       ruta_absoluta, tiempo=TIEMPO_COMPILACION)
        if codigo is None:
            return {"exito": False, "tipo_error": "tiempo",
                    "mensaje": "⏱️ Error: La compilación de C++ tardó demasiado."}
        if codigo != 0:
            return {"exito": False, "tipo_error": "compilacion",
                    "mensaje": "❌ Error de Compilación C++:\n" + AVISO_PRAGMA.sub("", errores)}

        codigo, salida, errores = _ejecutar([ejecutable], ruta_absoluta, entradas_usuario,
                                            memoria=LIMITE_MEMORIA_CPP)
        if codigo is None:
            return {"exito": False, "tipo_error": "tiempo",
                    "mensaje": "⏱️ Timeout: El programa C++ tardó demasiado en ejecutarse.\n" + salida}
        if errores:
            salida += "\n⚠️ Salida de error (stderr):\n" + errores
        return {"exito": True, "mensaje": salida + _motivo_terminacion(codigo)}
    finally:
        shutil.rmtree(carpeta_tmp, ignore_errors=True)


def compilar_java(ruta_absoluta, archivos_java, entradas_usuario):
    """Compila (javac) y ejecuta (java) un proyecto Java."""
    codigo, _, errores = _ejecutar(["javac", "-encoding", "utf-8"] + archivos_java,
                                   ruta_absoluta, tiempo=TIEMPO_COMPILACION)
    if codigo is None:
        return {"exito": False, "tipo_error": "tiempo",
                "mensaje": "⏱️ Error: La compilación de Java tardó demasiado."}
    if codigo != 0:
        mensaje = "❌ Error de Compilación Java:\n" + errores
        if _usa_package(ruta_absoluta, archivos_java):
            mensaje += ("\n💡 POOGraph no admite la instrucción 'package': todas las clases "
                        "del proyecto están en la misma carpeta. Elimina la línea 'package ...;'.")
        return {"exito": False, "tipo_error": "compilacion", "mensaje": mensaje}

    if "Main.java" not in archivos_java:
        return {"exito": False, "tipo_error": "estructura",
                "mensaje": "⚠️ Compiló bien, pero falta 'Main.java' para ejecutar."}

    codigo, salida, errores = _ejecutar(["java", MEMORIA_JVM, "-cp", ".", "Main"],
                                        ruta_absoluta, entradas_usuario)
    if codigo is None:
        return {"exito": False, "tipo_error": "tiempo",
                "mensaje": "⏱️ Timeout: El programa Java tardó demasiado.\n" + salida}
    if errores:
        salida += "\n⚠️ Errores ejecución:\n" + errores
    return {"exito": True, "mensaje": salida + _motivo_terminacion(codigo)}


def _usa_package(ruta_absoluta, archivos_java):
    patron = re.compile(r"^\s*package\s+[\w.]+\s*;", re.MULTILINE)
    for nombre in archivos_java:
        try:
            with open(os.path.join(ruta_absoluta, nombre), encoding="utf-8", errors="replace") as f:
                if patron.search(f.read()):
                    return True
        except OSError:
            pass
    return False
