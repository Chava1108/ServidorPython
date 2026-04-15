import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

#  Rutas de archivos
ruta_datos = os.path.join('..', 'datos', 'log_actividad.csv')

# Etiquetas de rendimiento
ETIQUETAS = {0: 'Bajo', 1: 'Medio', 2: 'Alto'}

def entrenar_modelo():
    #  Carga y preparación
    df = pd.read_csv(ruta_datos)
    df['fecha'] = pd.to_datetime(df['fecha'])

    # ============================================================
    # Ingeniería de Características (más variables para mayor varianza)
    # ============================================================

    # Conteo de acciones por tipo para cada usuario
    acciones_pivot = df.groupby('usuario')['accion'].value_counts().unstack(fill_value=0)

    features = pd.DataFrame(index=acciones_pivot.index)

    # 1. Total de acciones realizadas
    features['total_acciones'] = acciones_pivot.sum(axis=1)

    # 2. Errores detectados en el detalle (compilaciones fallidas, firmas duplicadas, etc.)
    features['errores'] = df.groupby('usuario')['detalle'].apply(
        lambda x: x.str.contains('Error|Fallo|error', case=False, na=False).sum()
    )

    # 3. Compilaciones exitosas vs fallidas
    features['compilaciones_ok'] = acciones_pivot.get('compiló_java', 0) + acciones_pivot.get('compiló_cpp', 0)
    features['tasa_error'] = features['errores'] / features['total_acciones'].replace(0, 1)

    # 4. Uso de conceptos POO avanzados
    features['uso_herencia'] = acciones_pivot.get('estableció_herencia', 0) + acciones_pivot.get('modificó_herencia', 0)
    features['uso_protected'] = df.groupby('usuario')['detalle'].apply(
        lambda x: x.str.contains('protected', case=False, na=False).sum()
    )

    # 5. Actividad de código (crear + modificar métodos y atributos)
    features['metodos_creados'] = acciones_pivot.get('creó_método', 0)
    features['atributos_creados'] = acciones_pivot.get('creó_atributo', 0)
    features['clases_creadas'] = acciones_pivot.get('creó_clase', 0)
    features['guardados'] = acciones_pivot.get('guardó_código', 0)

    # 6. Tiempo de sesión en minutos
    tiempos = df.groupby('usuario')['fecha'].agg(['min', 'max'])
    features['tiempo_sesion_min'] = (tiempos['max'] - tiempos['min']).dt.total_seconds() / 60

    # 7. Sesiones inactivas (indicador de abandono)
    features['sesiones_inactivas'] = acciones_pivot.get('cerró_sesión_inactividad', 0)

    # ============================================================
    # Generación de rendimiento con componente aleatorio
    # ============================================================
    # Score base: combinación ponderada de métricas (normalizado 0-100)
    np.random.seed(42)

    max_acciones = features['total_acciones'].max() if features['total_acciones'].max() > 0 else 1
    max_compilaciones = features['compilaciones_ok'].max() if features['compilaciones_ok'].max() > 0 else 1
    max_herencia = features['uso_herencia'].max() if features['uso_herencia'].max() > 0 else 1
    max_metodos = features['metodos_creados'].max() if features['metodos_creados'].max() > 0 else 1

    score = (
        (features['compilaciones_ok'] / max_compilaciones) * 25      # Compilaciones exitosas
        + (features['uso_herencia'] / max_herencia) * 20             # Uso de herencia
        + (features['metodos_creados'] / max_metodos) * 15           # Métodos creados
        + (features['total_acciones'] / max_acciones) * 15           # Actividad general
        + (features['uso_protected'] > 0).astype(int) * 10           # Usa protected
        - features['tasa_error'] * 20                                # Penalización por errores
        - (features['sesiones_inactivas'] * 2)                       # Penalización por inactividad
    )

    # Ruido proporcional: ±10% del rango del score para que no destruya el patrón
    rango_score = score.max() - score.min() if score.max() != score.min() else 1
    ruido = np.random.uniform(-0.10, 0.10, size=len(score)) * rango_score
    score_final = score + ruido

    # Clasificar en 3 niveles usando percentiles
    p33 = np.percentile(score_final, 33)
    p66 = np.percentile(score_final, 66)

    features['rendimiento'] = np.where(score_final <= p33, 0,       # Bajo
                              np.where(score_final <= p66, 1, 2))   # Medio / Alto

    # ============================================================
    # Imprimir tabla de features para revisión
    # ============================================================
    print("\n" + "=" * 80)
    print("TABLA DE CARACTERÍSTICAS POR USUARIO")
    print("=" * 80)
    columnas_mostrar = ['total_acciones', 'errores', 'tasa_error', 'compilaciones_ok',
                        'uso_herencia', 'uso_protected', 'clases_creadas', 'metodos_creados',
                        'tiempo_sesion_min', 'sesiones_inactivas', 'rendimiento']
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.float_format', '{:.2f}'.format)

    tabla = features[columnas_mostrar].copy()
    tabla['rendimiento_etq'] = tabla['rendimiento'].map(ETIQUETAS)
    print(tabla.to_string())

    print(f"\nDistribución de rendimiento:")
    print(features['rendimiento'].map(ETIQUETAS).value_counts().to_string())
    print(f"Total usuarios: {len(features)}")

    # ============================================================
    # Selección de Características y Entrenamiento
    # ============================================================
    columnas_X = ['tiempo_sesion_min', 'errores', 'tasa_error', 'compilaciones_ok',
                  'uso_herencia', 'uso_protected', 'total_acciones', 'guardados',
                  'sesiones_inactivas']
    X = features[columnas_X]
    y = features['rendimiento']

    #  División de datos (Entrenamiento 80% y Pruebas 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    #  Entrenamiento del Random Forest
    print("\n" + "=" * 80)
    print("ENTRENAMIENTO DEL MODELO RANDOM FOREST")
    print("=" * 80)
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    #  Evaluación
    predicciones = modelo.predict(X_test)
    print(f"\nPrecisión (Accuracy): {accuracy_score(y_test, predicciones):.2f}")
    print("\nReporte de Clasificación:")
    nombres_clases = [ETIQUETAS[i] for i in sorted(y.unique())]
    print(classification_report(y_test, predicciones, target_names=nombres_clases, zero_division=0))

    print("Matriz de Confusión:")
    print(confusion_matrix(y_test, predicciones))

    print("\nImportancia de Características:")
    importancias = sorted(zip(X.columns, modelo.feature_importances_), key=lambda x: x[1], reverse=True)
    for nombre, imp in importancias:
        barra = '#' * int(imp * 50)
        print(f"  {nombre:<22} {imp:.4f}  {barra}")

if __name__ == "__main__":
    entrenar_modelo()