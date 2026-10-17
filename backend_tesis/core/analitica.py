"""
Catálogo de eventos (verbos xAPI) y cálculos de analítica del aprendizaje.

Única fuente de verdad para el tablero (views.dashboard_analytics) y para el modelo
predictivo (modelo/caracteristicas.py). Es Python puro, sin Django, para que los
scripts del modelo puedan importarlo fuera del servidor.

Cada evento se maneja como una tupla (usuario, accion, detalle, fecha) con fecha
"aware" o en hora local; las funciones agrupan por la fecha que reciben.
"""
from collections import defaultdict

# ---------------------------------------------------------------------------
# Verbos que registra la plataforma
# ---------------------------------------------------------------------------
INICIO_SESION = "inició_sesión"
CIERRES_SESION = ("cerró_sesión_manual", "cerró_sesión_inactividad", "cerró_sesión")
CIERRE_INACTIVIDAD = "cerró_sesión_inactividad"

PREFIJO_COMPILACION_OK = "compiló_"      # compiló_java, compiló_cpp
PREFIJO_ERROR = "error_"                 # error_<tipo>_<lenguaje>; tipo: compilacion, estructura, tiempo, general

MOSTRAR_DIAGRAMA = "mostró_diagrama"
OCULTAR_DIAGRAMA = "ocultó_diagrama"
TOOLTIP = "consultó_tooltip"
PEGADO = "intentó_pegar_código"
GUARDADO = "guardó_código"

CREO_CLASE = "creó_clase"
AGREGO_ATRIBUTO = "agregó_atributo"
AGREGO_FUNCION = "agregó_función"
AGREGO_HERENCIA = "agregó_herencia"

# Origen de un guardado (se agrega al detalle como "| origen: <valor>")
ORIGENES_GUARDADO = ("manual", "ejecutar", "cambio_archivo", "inactividad")

# ---------------------------------------------------------------------------
# Formatos antiguos que siguen en la base de datos
# ---------------------------------------------------------------------------
# Verbos que solo generó simular_estudiantes.py: identifican a los usuarios sintéticos
VERBOS_SIMULADOR = ("compiló_proyecto", "editó_código", "MOSTRAR_DIAGRAMA", "OCULTAR_DIAGRAMA")
# Verbos de versiones anteriores del modelo, equivalentes a los actuales
EQUIVALENCIAS = {
    "estableció_herencia": AGREGO_HERENCIA,
    "modificó_herencia": AGREGO_HERENCIA,
    "creó_método": AGREGO_FUNCION,
    "creó_atributo": AGREGO_ATRIBUTO,
    "MOSTRAR_DIAGRAMA": MOSTRAR_DIAGRAMA,
    "OCULTAR_DIAGRAMA": OCULTAR_DIAGRAMA,
}

LIMITE_SESION_MIN = 120    # una sesión más larga se considera atípica y se recorta
LIMITE_DIAGRAMA_MIN = 60


def normalizar(accion, detalle):
    """
    Devuelve el verbo actual equivalente a un evento guardado con un formato anterior.
    - Antes, mostrar/ocultar el diagrama se guardaba como consultó_tooltip con la palabra
      'MOSTRAR_DIAGRAMA' u 'OCULTAR_DIAGRAMA' en el detalle.
    - El simulador usó 'compiló_proyecto' tanto para éxitos como para errores.
    """
    detalle = detalle or ""
    if accion == TOOLTIP and "_DIAGRAMA" in detalle:
        return MOSTRAR_DIAGRAMA if "MOSTRAR_DIAGRAMA" in detalle else OCULTAR_DIAGRAMA
    if accion == "compiló_proyecto":
        return "error_compilacion_legado" if "error" in detalle.lower() else "compiló_legado"
    return EQUIVALENCIAS.get(accion, accion)


def es_compilacion_ok(verbo):
    return verbo.startswith(PREFIJO_COMPILACION_OK)


def es_error(verbo):
    return verbo.startswith(PREFIJO_ERROR)


def tipo_error(verbo):
    """error_compilacion_cpp -> 'compilacion'; error_tiempo_java -> 'tiempo'."""
    partes = verbo.split("_")
    return partes[1] if len(partes) >= 3 else "general"


def origen_guardado(detalle):
    """Origen de un guardó_código; los registros anteriores al cambio no lo tienen."""
    detalle = detalle or ""
    if "origen:" not in detalle:
        return "sin_dato"
    return detalle.rsplit("origen:", 1)[1].strip().split()[0]


def _por_usuario(eventos):
    """Agrupa eventos ya normalizados [(usuario, verbo, detalle, fecha)] por usuario y en orden."""
    grupos = defaultdict(list)
    for e in eventos:
        grupos[e[0]].append(e)
    for lista in grupos.values():
        lista.sort(key=lambda e: e[3])
    return grupos


def sesiones(eventos):
    """
    Reconstruye las sesiones de cada usuario.
    Una sesión empieza en inició_sesión y termina en el primer cierre de sesión.
    Si antes llega otro inicio de sesión o se acaban los eventos (el alumno cerró la
    pestaña), termina en su último evento registrado. Devuelve una lista de
    dict(usuario, inicio, fin, minutos, con_cierre).
    """
    resultado = []
    for usuario, lista in _por_usuario(eventos).items():
        inicio = ultimo = None
        for _, verbo, _, fecha in lista:
            if verbo == INICIO_SESION:
                if inicio is not None:
                    resultado.append(_sesion(usuario, inicio, ultimo, False))
                inicio = ultimo = fecha
            elif inicio is not None:
                ultimo = fecha
                if verbo in CIERRES_SESION:
                    resultado.append(_sesion(usuario, inicio, fecha, True))
                    inicio = ultimo = None
        if inicio is not None:
            resultado.append(_sesion(usuario, inicio, ultimo, False))
    return resultado


def _sesion(usuario, inicio, fin, con_cierre):
    minutos = min((fin - inicio).total_seconds() / 60.0, LIMITE_SESION_MIN)
    return {"usuario": usuario, "inicio": inicio, "fin": fin, "minutos": minutos, "con_cierre": con_cierre}


def intervalos_diagrama(eventos):
    """
    Intervalos con el diagrama visible: de mostró_diagrama al siguiente ocultó_diagrama,
    cierre o inicio de sesión. Si no hay ninguno (pestaña cerrada), hasta el último
    evento del usuario en ese tramo. Devuelve dict(usuario, inicio, minutos).
    """
    resultado = []
    fin_tramo = (OCULTAR_DIAGRAMA, INICIO_SESION) + CIERRES_SESION
    for usuario, lista in _por_usuario(eventos).items():
        visible_desde = ultimo = None
        for _, verbo, _, fecha in lista:
            if visible_desde is not None and verbo in fin_tramo:
                fin = fecha if verbo != INICIO_SESION else ultimo
                resultado.append(_intervalo(usuario, visible_desde, fin))
                visible_desde = None
            if verbo == MOSTRAR_DIAGRAMA and visible_desde is None:
                visible_desde = fecha
            ultimo = fecha
        if visible_desde is not None:
            resultado.append(_intervalo(usuario, visible_desde, ultimo))
    return resultado


def _intervalo(usuario, inicio, fin):
    minutos = min(max((fin - inicio).total_seconds() / 60.0, 0), LIMITE_DIAGRAMA_MIN)
    return {"usuario": usuario, "inicio": inicio, "minutos": minutos}
