"""
Ingeniería de características compartida por modelo_random_forest.py y seleccion_caracteristicas.py.

Usa el mismo catálogo de verbos que el tablero (core/analitica.py), de modo que el modelo y el
dashboard cuentan los mismos eventos. Los registros con verbos antiguos se normalizan.
"""
import os
import sys

import numpy as np
import pandas as pd

# core/analitica.py es Python puro: se importa sin cargar Django
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core'))
import analitica  # noqa: E402

DIR_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
CSV_REAL = os.path.join(DIR_DATOS, 'log_actividad_real.csv')       # generado por exportar_logs.py
CSV_SINTETICO = os.path.join(DIR_DATOS, 'log_actividad.csv')        # datos de prueba del simulador

ETIQUETAS = {0: 'Bajo', 1: 'Medio', 2: 'Alto'}


CSV_CALIFICACIONES = os.path.join(DIR_DATOS, 'calificaciones.csv')   # generado por exportar_logs.py
UMBRAL_APROBADO = 70   # variable objetivo binaria: post-test >= 70


def cargar_logs(ruta=None, grupos=None, dias=None):
    """
    Lee el CSV de logs (por defecto el real; si no existe, el sintético con un aviso).
    grupos: lista de grupos a conservar (p. ej. ['experimental']); requiere la columna 'grupo'.
    dias: conserva solo los primeros N días de actividad de cada alumno (predicción temprana).
    """
    if ruta is None:
        ruta = CSV_REAL if os.path.exists(CSV_REAL) else CSV_SINTETICO
    if ruta == CSV_SINTETICO:
        print("AVISO: se usan los datos SINTÉTICOS de datos/log_actividad.csv. "
              "Para los datos reales ejecuta primero modelo/exportar_logs.py en el servidor.\n")
    df = pd.read_csv(ruta)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['usuario'] = df['usuario'].astype(str)
    df['detalle'] = df['detalle'].fillna('')
    if grupos and 'grupo' in df.columns:
        df = df[df['grupo'].isin(grupos)]
    if dias:
        inicio = df.groupby('usuario')['fecha'].transform('min')
        df = df[df['fecha'] < inicio + pd.Timedelta(days=dias)]
    print(f"Logs cargados de {ruta}: {len(df)} eventos, {df['usuario'].nunique()} usuarios"
          + (f" (grupos: {', '.join(grupos)})" if grupos else "")
          + (f" (primeros {dias} días)" if dias else "") + "\n")
    return df


def etiqueta_post_test(f, ruta=CSV_CALIFICACIONES, umbral=UMBRAL_APROBADO):
    """
    Variable objetivo real (A-18): 1 si el post-test del alumno es >= umbral, 0 si no.
    Devuelve una Serie alineada con f; los alumnos sin post-test quedan como NaN.
    """
    if not os.path.exists(ruta):
        return None
    notas = pd.read_csv(ruta, dtype={'usuario': str}).set_index('usuario')
    post = notas['post'].reindex(f.index)
    return (post >= umbral).astype(float).where(post.notna())


def construir(df):
    """Devuelve un DataFrame con una fila de características por usuario."""
    df = df.copy()
    df['verbo'] = [analitica.normalizar(a, d) for a, d in zip(df['accion'], df['detalle'])]
    eventos = list(zip(df['usuario'], df['verbo'], df['detalle'], df['fecha']))
    conteo = df.groupby('usuario')['verbo'].value_counts().unstack(fill_value=0)

    def col(verbo):
        return conteo[verbo] if verbo in conteo.columns else 0

    def contar(filtro):
        return df[filtro].groupby('usuario').size().reindex(conteo.index, fill_value=0)

    f = pd.DataFrame(index=conteo.index)
    f['total_acciones'] = conteo.sum(axis=1)

    # Compilación
    f['compilaciones_ok'] = contar(df['verbo'].map(analitica.es_compilacion_ok))
    f['errores'] = contar(df['verbo'].map(analitica.es_error))
    intentos = (f['compilaciones_ok'] + f['errores']).replace(0, 1)
    f['tasa_error'] = f['errores'] / intentos          # errores por intento de compilación

    # Conceptos de POO
    f['clases_creadas'] = col(analitica.CREO_CLASE)
    f['atributos_creados'] = col(analitica.AGREGO_ATRIBUTO)
    f['metodos_creados'] = col(analitica.AGREGO_FUNCION)
    f['uso_herencia'] = col(analitica.AGREGO_HERENCIA)
    # El nivel de acceso está en el detalle desde la versión de octubre de 2026
    f['uso_protected'] = contar(df['verbo'].isin([analitica.AGREGO_ATRIBUTO, analitica.AGREGO_FUNCION])
                                & df['detalle'].str.contains('protected', case=False))

    # Trabajo en el editor (sin los guardados automáticos al ejecutar o cambiar de archivo)
    origen = df['detalle'].map(analitica.origen_guardado)
    f['guardados'] = contar((df['verbo'] == analitica.GUARDADO)
                            & ~origen.isin(['ejecutar', 'cambio_archivo', 'inactividad']))
    f['tooltips'] = col(analitica.TOOLTIP)
    f['intentos_pegado'] = col(analitica.PEGADO)

    # Tiempo (sesiones reconstruidas igual que en el tablero)
    ses = pd.DataFrame(analitica.sesiones(eventos), columns=['usuario', 'inicio', 'fin', 'minutos', 'con_cierre'])
    f['sesiones'] = ses.groupby('usuario').size().reindex(f.index, fill_value=0)
    f['tiempo_sesion_min'] = ses.groupby('usuario')['minutos'].sum().reindex(f.index, fill_value=0.0)
    f['sesiones_inactivas'] = col(analitica.CIERRE_INACTIVIDAD)
    dia = pd.DataFrame(analitica.intervalos_diagrama(eventos), columns=['usuario', 'inicio', 'minutos'])
    f['tiempo_diagrama_min'] = dia.groupby('usuario')['minutos'].sum().reindex(f.index, fill_value=0.0)
    return f


def etiqueta_heuristica(f, semilla=42):
    """
    ETIQUETA PROVISIONAL (acción A-18 del plan): puntuación ponderada de la actividad, con ruido,
    dividida en terciles. Debe sustituirse por la calificación del post-test o la ganancia de Hake.
    """
    def norm(serie):
        maximo = serie.max()
        return serie / maximo if maximo > 0 else serie * 0

    np.random.seed(semilla)
    score = (norm(f['compilaciones_ok']) * 25 + norm(f['uso_herencia']) * 20
             + norm(f['metodos_creados']) * 15 + norm(f['total_acciones']) * 15
             + (f['uso_protected'] > 0).astype(int) * 10
             - f['tasa_error'] * 20 - f['sesiones_inactivas'] * 2)
    rango = (score.max() - score.min()) or 1
    score = score + np.random.uniform(-0.10, 0.10, size=len(score)) * rango
    p33, p66 = np.percentile(score, 33), np.percentile(score, 66)
    return pd.Series(np.where(score <= p33, 0, np.where(score <= p66, 1, 2)), index=f.index)
