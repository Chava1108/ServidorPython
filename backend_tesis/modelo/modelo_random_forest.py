import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. Rutas de archivos
ruta_datos = os.path.join('..', 'datos', 'log_actividad.csv')

def entrenar_modelo():
    # 2. Carga y preparación (repetimos la agregación de la Actividad I)
    df = pd.read_csv(ruta_datos)
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Ingeniería de Características
    features = df.groupby('usuario').agg(
        errores=('detalle', lambda x: x.str.contains('Error', case=False).sum()),
        uso_protected=('detalle', lambda x: x.str.contains('protected', case=False).sum())
    )
    tiempos = df.groupby('usuario')['fecha'].agg(['min', 'max'])
    features['tiempo_sesion_min'] = (tiempos['max'] - tiempos['min']).dt.total_seconds() / 60

    # 3. Selección de Características (Las 3 mejores según Relief)

    X = features[['tiempo_sesion_min', 'errores', 'uso_protected']]
    
    # Generamos la etiqueta objetivo (Rendimiento) de forma lógica para la prueba

    features['rendimiento'] = np.where(features['errores'] > 2, 0, 
                                     np.where(features['uso_protected'] > 1, 2, 1))
    y = features['rendimiento']

    # 4. División de datos (Entrenamiento 80% y Pruebas 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    # 5. Entrenamiento del Random Forest
    print("--- Entrenando Modelo Random Forest ---")
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # 6. Evaluación
    predicciones = modelo.predict(X_test)
    print(f"\nPrecisión del modelo (Accuracy): {accuracy_score(y_test, predicciones):.2f}")
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, predicciones))

    print("\n--- Importancia Interna del Bosque ---")
    for nombre, imp in zip(X.columns, modelo.feature_importances_):
        print(f"{nombre}: {imp:.4f}")

if __name__ == "__main__":
    entrenar_modelo()