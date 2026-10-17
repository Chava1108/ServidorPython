"""
Modelo predictivo de rendimiento (Random Forest) a partir de los logs de interacción.

Uso (desde backend_tesis/modelo):
    python modelo_random_forest.py                 # datos/log_actividad_real.csv (o el sintético si no existe)
    python modelo_random_forest.py ruta/logs.csv   # otro archivo exportado
"""
import sys

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import LeaveOneOut, cross_val_predict, train_test_split

from caracteristicas import ETIQUETAS, cargar_logs, construir, etiqueta_heuristica

MIN_PARTICION = 50   # por debajo de este número de usuarios se usa validación cruzada leave-one-out

COLUMNAS_X = ['tiempo_sesion_min', 'errores', 'tasa_error', 'compilaciones_ok',
              'uso_herencia', 'uso_protected', 'total_acciones', 'guardados',
              'sesiones_inactivas', 'tiempo_diagrama_min', 'tooltips']


def entrenar_modelo(ruta=None):
    features = construir(cargar_logs(ruta))
    # PROVISIONAL (A-18): sustituir por la calificación del post-test cuando se aplique
    features['rendimiento'] = etiqueta_heuristica(features)

    print("=" * 80)
    print("TABLA DE CARACTERÍSTICAS POR USUARIO")
    print("=" * 80)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 220)
    pd.set_option('display.float_format', '{:.2f}'.format)
    tabla = features[COLUMNAS_X + ['rendimiento']].copy()
    tabla['rendimiento_etq'] = tabla['rendimiento'].map(ETIQUETAS)
    print(tabla.to_string())
    print("\nDistribución de rendimiento:")
    print(features['rendimiento'].map(ETIQUETAS).value_counts().to_string())
    print(f"Total usuarios: {len(features)}")

    if len(features) < 10:
        print("\nHay menos de 10 usuarios: no es posible entrenar y evaluar el modelo con fiabilidad.")
        return

    X, y = features[COLUMNAS_X], features['rendimiento']

    print("\n" + "=" * 80)
    print("ENTRENAMIENTO DEL MODELO RANDOM FOREST")
    print("=" * 80)
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)

    if len(features) < MIN_PARTICION:
        # Con pocos alumnos, una partición 80/20 deja 2 o 3 casos de prueba: se evalúa cada
        # alumno con un modelo entrenado con todos los demás (validación cruzada leave-one-out)
        print(f"\n{len(features)} usuarios: evaluación con validación cruzada leave-one-out")
        y_test = y
        predicciones = cross_val_predict(modelo, X, y, cv=LeaveOneOut())
        modelo.fit(X, y)
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
        modelo.fit(X_train, y_train)
        predicciones = modelo.predict(X_test)

    print(f"\nPrecisión (Accuracy): {accuracy_score(y_test, predicciones):.2f}")
    print("\nReporte de Clasificación:")
    clases = sorted(y.unique())
    print(classification_report(y_test, predicciones, labels=clases,
                                target_names=[ETIQUETAS[i] for i in clases], zero_division=0))
    print("Matriz de Confusión:")
    print(confusion_matrix(y_test, predicciones, labels=clases))

    print("\nImportancia de Características:")
    for nombre, imp in sorted(zip(X.columns, modelo.feature_importances_), key=lambda x: x[1], reverse=True):
        print(f"  {nombre:<22} {imp:.4f}  {'#' * int(imp * 50)}")


if __name__ == "__main__":
    entrenar_modelo(sys.argv[1] if len(sys.argv) > 1 else None)
