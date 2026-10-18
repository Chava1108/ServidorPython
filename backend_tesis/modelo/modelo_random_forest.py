"""
Modelos predictivos del rendimiento a partir de los logs de interacción:
Regresión logística y Random Forest, comparados contra la línea base (clase mayoritaria).

Variable objetivo:
  - Real (A-18): post-test >= 70, leído de datos/calificaciones.csv (exportar_logs.py).
  - Si aún no hay post-tests suficientes, una etiqueta heurística PROVISIONAL (con aviso).

Uso (desde backend_tesis/modelo):
    python modelo_random_forest.py                         # todos los alumnos reales
    python modelo_random_forest.py --grupo experimental    # solo el grupo experimental
    python modelo_random_forest.py --dias 14               # predicción temprana: 2 primeras semanas
    python modelo_random_forest.py --logs ruta.csv
"""
import argparse

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import LeaveOneOut, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from caracteristicas import ETIQUETAS, UMBRAL_APROBADO, cargar_logs, construir, etiqueta_heuristica, etiqueta_post_test

COLUMNAS_X = ['tiempo_sesion_min', 'errores', 'tasa_error', 'compilaciones_ok',
              'uso_herencia', 'uso_protected', 'total_acciones', 'guardados',
              'sesiones_inactivas', 'tiempo_diagrama_min', 'tooltips']
MIN_PARTICION = 50    # por debajo de este número de alumnos: leave-one-out; si no, 5 particiones
MIN_ALUMNOS = 10


def preparar(args):
    features = construir(cargar_logs(args.logs, [args.grupo] if args.grupo else None, args.dias))
    real = etiqueta_post_test(features)
    if real is not None and real.notna().sum() >= MIN_ALUMNOS:
        features = features[real.notna()].copy()
        features['rendimiento'] = real.dropna().astype(int)
        nombres = {0: f'Post < {UMBRAL_APROBADO}', 1: f'Post >= {UMBRAL_APROBADO}'}
        print(f"Variable objetivo REAL: post-test >= {UMBRAL_APROBADO} ({len(features)} alumnos con post-test)\n")
    else:
        features['rendimiento'] = etiqueta_heuristica(features)
        nombres = ETIQUETAS
        print("AVISO: no hay suficientes post-tests; se usa la etiqueta heurística PROVISIONAL.\n")
    return features, nombres


def evaluar(nombre, modelo, X, y, cv, nombres):
    pred = cross_val_predict(modelo, X, y, cv=cv)
    clases = sorted(y.unique())
    print("-" * 80)
    print(nombre)
    print("-" * 80)
    print(f"Exactitud: {accuracy_score(y, pred):.2f}   F1 macro: {f1_score(y, pred, average='macro', zero_division=0):.2f}")
    print(classification_report(y, pred, labels=clases, target_names=[nombres[c] for c in clases], zero_division=0))
    print("Matriz de confusión (filas = real, columnas = predicho):")
    print(confusion_matrix(y, pred, labels=clases))
    return f1_score(y, pred, average='macro', zero_division=0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--logs', default=None)
    p.add_argument('--grupo', default=None, help='experimental, control, pruebas...')
    p.add_argument('--dias', type=int, default=None, help='usar solo los primeros N días de actividad')
    args = p.parse_args()

    features, nombres = preparar(args)
    pd.set_option('display.width', 220)
    pd.set_option('display.float_format', '{:.2f}'.format)
    print(features[COLUMNAS_X + ['rendimiento']].to_string())
    print("\nDistribución:", features['rendimiento'].map(nombres).value_counts().to_dict())

    if len(features) < MIN_ALUMNOS or features['rendimiento'].nunique() < 2:
        print(f"\nSe necesitan al menos {MIN_ALUMNOS} alumnos y dos clases para entrenar y evaluar.")
        return

    X, y = features[COLUMNAS_X].astype(float), features['rendimiento']
    minoritaria = y.value_counts().min()
    if len(features) < MIN_PARTICION or minoritaria < 5:
        cv, desc = LeaveOneOut(), "validación cruzada leave-one-out"
    else:
        cv, desc = StratifiedKFold(n_splits=5, shuffle=True, random_state=42), "validación cruzada estratificada de 5 particiones"
    print(f"\n{len(features)} alumnos · evaluación con {desc}\n")

    resultados = {
        "Línea base (clase mayoritaria)": evaluar("LÍNEA BASE (clase mayoritaria)",
                                                  DummyClassifier(strategy='most_frequent'), X, y, cv, nombres),
        "Regresión logística": evaluar("MODELO 1 · REGRESIÓN LOGÍSTICA",
                                       make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight='balanced')),
                                       X, y, cv, nombres),
        "Random Forest": evaluar("MODELO 2 · RANDOM FOREST",
                                 RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced'),
                                 X, y, cv, nombres),
    }

    print("=" * 80)
    print("COMPARACIÓN (F1 macro)")
    for nombre, f1 in resultados.items():
        print(f"  {nombre:<32} {f1:.2f}")

    rf = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced').fit(X, y)
    print("\nImportancia de características (Random Forest entrenado con todos los alumnos):")
    for nombre, imp in sorted(zip(X.columns, rf.feature_importances_), key=lambda x: x[1], reverse=True):
        print(f"  {nombre:<22} {imp:.4f}  {'#' * int(imp * 50)}")


if __name__ == "__main__":
    main()
